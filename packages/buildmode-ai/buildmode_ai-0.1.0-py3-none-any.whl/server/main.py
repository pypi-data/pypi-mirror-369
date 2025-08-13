"""Main entrypoint for the BuildMode.AI backend.

This module wires up the FastAPI application used by the project.  It loads
configuration, attaches middleware for security, and mounts all service
routers.

Run with ``uvicorn server.main:app`` (or ``python -m server.main``) to start
the API server.
"""

from contextlib import asynccontextmanager
from datetime import datetime
import logging
import os
import uuid
from collections import defaultdict, deque
from time import time
from typing import Deque, Dict, DefaultDict
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import openai
from pydantic import BaseModel
from qdrant_client.http.models import FieldCondition, Filter, MatchValue
from server.agents.utils import normalize_input
from server.services.qdrant_service import get_qdrant_service
from server.app_config import AppConfig

# --- Configuration & Initial Setup ---
# Load environment variables from a .env file for local development.
# In Railway, these are set directly in the dashboard.
load_dotenv()


def setup_logging() -> None:
    """Configure application-wide logging.

    Logging setup is isolated to avoid side effects when this module is
    imported. This function should be called explicitly on application
    startup or when running this module directly.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


# --- Environment Variable Loading ---
# Centralized configuration for clarity

# Centralized names for defaults used across helpers
app_config = AppConfig()
QDRANT_COLLECTION_NAME = app_config.qdrant_collection_name

# --- Module-level runtime state ---
# These are initialized once and then referenced in the lifespan function.
banned_ips: Dict[str, float] = {}
not_found_events: DefaultDict[str, Deque[float]] = defaultdict(
    lambda: deque(maxlen=app_config.not_found_threshold)
)
NOT_FOUND_THRESHOLD = app_config.not_found_threshold

# --- App Lifespan Manager (Startup & Shutdown Logic) ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events.

    Initializes database connections and ensures necessary resources are
    available.

    Args:
        app: The FastAPI application instance.

    Yields:
        None. The application continues running while the context is active.
    """
    setup_logging()
    logging.info("Application startup: Initializing clients...")

    missing_env_vars = [
        name
        for name, value in (
            ("QDRANT_URL", app_config.qdrant_url),
            ("QDRANT_API_KEY", app_config.qdrant_api_key),
            ("OPENAI_API_KEY", app_config.openai_api_key),
        )
        if not value
    ]
    if missing_env_vars:
        logging.error(
            "Missing required environment variables: %s",
            ", ".join(missing_env_vars),
        )

    app.state.config = app_config
    app.state.banned_ips = banned_ips
    app.state.not_found_events = not_found_events
    app.state.send_security_alert = send_security_alert

    # Initialize OpenAI and Qdrant clients and store them in the app state.
    # In the test environment we avoid network calls during startup so
    # tests can monkeypatch services without the app trying to connect.
    service = get_qdrant_service()
    if (
        normalize_input(os.getenv("NODE_ENV", "development")) == "test"
        or not app_config.qdrant_url
    ):
        logging.info(
            "Test or missing QDRANT_URL: skipping OpenAI init; "
            "using qdrant_service client"
        )
        app.state.openai_client = None
        app.state.qdrant_client = service.client
    else:
        app.state.openai_client = openai.AsyncOpenAI(
            api_key=app_config.openai_api_key
        )
        # Use the centralized QdrantService instance which handles a mock
        # fallback and retry wrappers.
        app.state.qdrant_client = service.client

    # --- Ensure Qdrant Collection Exists (Idempotent) ---
    # This block checks for the collection and creates it if it's missing.
    if app.state.qdrant_client:
        try:
            # Use the QdrantService helpers which encapsulate client logic
            if not service.collection_exists(
                app_config.qdrant_collection_name
            ):
                logging.warning(
                    "Collection '%s' not found. Creating it now...",
                    app_config.qdrant_collection_name,
                )
                service.create_collection(
                    collection_name=app_config.qdrant_collection_name,
                    vector_size=app_config.embedding_dimension,
                    distance="cosine",
                )
                logging.info(
                    "Collection '%s' created successfully.",
                    app_config.qdrant_collection_name,
                )
            else:
                logging.info(
                    "Collection '%s' already exists.",
                    app_config.qdrant_collection_name,
                )
        except Exception as e:
            logging.error(f"Could not connect to or set up Qdrant. Error: {e}")
            # In a real-world scenario, you might want to prevent the app from
            # starting if the vector DB is unavailable.

    yield

    logging.info("Application shutdown.")


# --- FastAPI App Initialization ---
app = FastAPI(
    title="BuildMode.AI Core API",
    description=(
        "Core backend services for BuildMode.AI, including AI memory and chat."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# Ensure essential state is available even if startup events are skipped
app.state.config = app_config
app.state.banned_ips = {}
app.state.not_found_events = defaultdict(
    lambda: deque(maxlen=app_config.not_found_threshold)
)

# --- Static Files ---
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount(
    "/assets",
    StaticFiles(directory=STATIC_DIR / "assets"),
    name="assets",
)
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

# --- Security Middleware ---
# Runtime security-related state is stored on the application instance.


async def send_security_alert(ip: str, count: int) -> None:
    """Send a security alert when suspicious activity is detected.

    Logs a warning with the offending IP address and request count.

    Args:
        ip: The client IP address that triggered the alert.
        count: Number of requests received within the monitoring window.
    """
    logging.warning(
        f"Security alert triggered for IP {ip}: {count} "
        "404 responses within 60 seconds"
    )


app.state.send_security_alert = send_security_alert


__all__ = [
    "app",
    "send_security_alert",
    "banned_ips",
    "not_found_events",
    "NOT_FOUND_THRESHOLD",
    "QDRANT_COLLECTION_NAME",
]


@app.middleware("http")
async def enforce_ip_bans(request: Request, call_next):
    """Block requests from banned IP addresses and clean up expired bans."""
    now = time()
    banned_ips = request.app.state.banned_ips

    # Remove expired bans
    expired = [ip for ip, expiry in banned_ips.items() if expiry <= now]
    for ip in expired:
        del banned_ips[ip]

    client_ip = request.client.host
    if client_ip in banned_ips and banned_ips[client_ip] > now:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too Many Requests"},
        )

    return await call_next(request)


@app.middleware("http")
async def block_sensitive_paths(request: Request, call_next):
    """Prevent access to dotfiles and other sensitive resources.

    We rely on configurable regular expressions rather than hardcoded file
    names so that a single pattern can catch encoded or nested attempts to
    read secrets like ``.env`` or ``.git``.
    """
    path = os.path.normpath(request.url.path)
    patterns = request.app.state.config.forbidden_path_patterns
    # Using regex allows us to match attempts at path traversal or encoded
    # variants (e.g., ``..%2F.env``) that simple string comparisons miss.
    if any(pattern.search(path) for pattern in patterns):
        logging.warning(
            f"Blocked access attempt to sensitive path: {path} "
            f"from IP: {request.client.host}"
        )
        # Tests expect a short `Forbidden` detail string here.
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    response = await call_next(request)
    return response


@app.exception_handler(404)
async def handle_not_found(request: Request, exc):
    """Handle 404 errors and track repeated occurrences per IP.

    Repeated 404s are a common sign of bots scanning for vulnerable
    endpoints.  By keeping a short-lived history per IP we can surface
    suspicious activity without permanently storing visitor data.
    """
    ip = request.client.host if request.client else "unknown"
    now = time()
    cutoff = now - 60

    events_map: Dict[str, Deque[float]] = request.app.state.not_found_events
    threshold = request.app.state.config.not_found_threshold

    # Drop IPs that haven't triggered a 404 within the TTL window to avoid
    # unbounded growth of the tracking dictionary.
    for ip_addr, timestamps in list(events_map.items()):
        if timestamps and timestamps[-1] < cutoff:
            del events_map[ip_addr]

    events = events_map[ip]
    events.append(now)

    while events and events[0] < cutoff:
        events.popleft()
    if len(events) >= threshold:
        await request.app.state.send_security_alert(ip, threshold)
        events.clear()
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


# --- CORS (Cross-Origin Resource Sharing) Middleware ---
# CORRECTION: Removed the redundant custom origin enforcement.
# The standard CORSMiddleware handles this correctly and more securely.
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Include route modules ---
# Mount routers under the common `/api` prefix so tests and clients
# can rely on predictable API paths (e.g. `/api/tasks/create`).
try:
    from server.routes import tasks as _tasks
    from server.routes import memory as _memory
    from server.routes import chat as _chat
    from server.routes import openai_proxy as _openai_proxy
    from server.routes import phases as _phases
    from server.routes import planner as _planner
    from server.routes import epics as _epics
    from server.routes import goals as _goals
    from server.routes import terminal as _terminal
    from server.routes import test_runner as _test_runner
    from server.routes import webhooks as _webhooks
    from server.routes import vision as _vision
    from server.routes import profile as _profile
except Exception as exc:
    logging.error(
        "Failed to import optional route modules "
        "(e.g., server.routes.tasks). "
        "Missing dependencies such as httpx may be the cause. "
        "Some routes will be unavailable and POST requests may hit the SPA "
        "fallback, returning 405 responses. Error: %s",
        exc,
    )
    (
        _tasks,
        _memory,
        _chat,
        _openai_proxy,
        _phases,
        _planner,
        _epics,
        _goals,
        _terminal,
        _test_runner,
        _webhooks,
        _vision,
        _profile,
    ) = (None,) * 13

try:
    from server.routes import kairos as _kairos
except Exception as exc:
    logging.error("Failed to load Kairos router: %s", exc)
    _kairos = None

# Ensure essential routers like tasks are available
# even if grouped import fails
if _tasks is None:
    try:
        from server.routes import tasks as _tasks
    except Exception:
        _tasks = None

try:
    from server.services import runtime_logs as _runtime_logs
except Exception:
    _runtime_logs = None

if _tasks:
    app.include_router(_tasks.router, prefix="/api")
if _memory:
    # memory router uses a different symbol name
    try:
        app.include_router(_memory.memory_router, prefix="/api")
    except Exception:
        app.include_router(_memory.router, prefix="/api")
if _chat:
    app.include_router(_chat.router, prefix="/api")
if _openai_proxy:
    app.include_router(_openai_proxy.router, prefix="/api")
if _kairos:
    app.include_router(_kairos.router, prefix="/api")
if _phases:
    app.include_router(_phases.router, prefix="/api")
if _planner:
    app.include_router(_planner.router, prefix="/api")
if _epics:
    app.include_router(_epics.router, prefix="/api")
if _goals:
    app.include_router(_goals.router, prefix="/api")
if _terminal:
    app.include_router(_terminal.router, prefix="/api")
if _test_runner:
    app.include_router(_test_runner.router, prefix="/api")
if _webhooks:
    app.include_router(_webhooks.router, prefix="/api")
if _vision:
    app.include_router(_vision.router, prefix="/api")
if _profile:
    app.include_router(_profile.router, prefix="/api")
if _runtime_logs:
    app.include_router(_runtime_logs.router, prefix="/api")


# --- Pydantic Models for API Data Structure ---


class ChatMessage(BaseModel):
    user_id: str
    text: str


class ChatResponse(BaseModel):
    ai_response: str


# --- Chat Helper Functions ---


async def generate_query_vector(
    client, text: str, embedding_model: str = app_config.embedding_model
) -> list[float]:
    """Generate an embedding vector for the incoming message."""
    embedding_response = await client.embeddings.create(
        model=embedding_model, input=text
    )
    return embedding_response.data[0].embedding


def retrieve_relevant_memories(
    client,
    user_id: str,
    query_vector: list[float],
    collection_name: str = QDRANT_COLLECTION_NAME,
) -> list[str]:
    """Fetch relevant memories from Qdrant for context."""
    search_results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        query_filter=Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            ]
        ),
        limit=5,
    )
    return (
        [hit.payload["text"] for hit in search_results]
        if search_results
        else []
    )


async def generate_ai_response(
    client,
    message_text: str,
    memories: list[str],
    model: str = app_config.chat_completion_model,
) -> str:
    """Produce a chat completion using retrieved memories."""
    memory_context = "\n".join(memories)
    system_prompt = (
        "You are BuildMode, a supportive and insightful AI life coach. "
        "You are talking to a user who you have spoken with before. "
        "Here are some relevant memories from your past conversations "
        "with them, which you should use to inform your response:\n"
        f"--- Past Memories ---\n{memory_context}\n"
        "--- End of Memories ---\n\n"
        "Based on these memories, respond to the user's latest message "
        "in a helpful and personal way. "
        "If there are no memories, greet them warmly as if it's "
        "your first time talking."
    )
    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message_text},
        ],
    )
    return completion.choices[0].message.content


def store_memory(
    client,
    user_id: str,
    text: str,
    query_vector: list[float],
    collection_name: str = QDRANT_COLLECTION_NAME,
) -> None:
    """Persist the latest message and its embedding to Qdrant."""
    client.upsert(
        collection_name=collection_name,
        points=[
            {
                "id": str(uuid.uuid4()),
                "vector": query_vector,
                "payload": {
                    "user_id": user_id,
                    "text": text,
                    "created_at": datetime.utcnow().isoformat(),
                },
            }
        ],
        wait=True,
    )


def format_chat_response(ai_text: str) -> ChatResponse:
    """Format the AI text into the response model."""
    return ChatResponse(ai_response=ai_text)


# --- API Endpoints ---


@app.get("/api/health", tags=["Health Check"])
def api_health():
    """Return the service health status."""
    return {"message": "BuildMode AI Service is running."}


@app.get("/health", tags=["Health Check"])
def health():
    """Return a basic health status for tests."""
    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    """Simple health check endpoint used by platforms like Railway."""
    return {"ok": True}


@app.get("/qdrant/test")
def qdrant_test():
    """Check connectivity to the Qdrant service."""
    service = get_qdrant_service()
    result = service.health_check()
    if result.get("status") == "healthy":
        return {
            "status": "success",
            "message": "Qdrant is connected and operational",
        }
    return {"status": "error", "message": "Qdrant health check failed"}


@app.post("/chat", response_model=ChatResponse, tags=["AI Chat"])
async def handle_chat_message(message: ChatMessage, request: Request):
    """Process chat messages by delegating to helper functions."""
    config = request.app.state.config
    try:
        query_vector = await generate_query_vector(
            request.app.state.openai_client,
            message.text,
            config.embedding_model,
        )
        memories = retrieve_relevant_memories(
            request.app.state.qdrant_client,
            message.user_id,
            query_vector,
            config.qdrant_collection_name,
        )
        ai_response = await generate_ai_response(
            request.app.state.openai_client,
            message.text,
            memories,
            config.chat_completion_model,
        )
        store_memory(
            request.app.state.qdrant_client,
            message.user_id,
            message.text,
            query_vector,
            config.qdrant_collection_name,
        )
        return format_chat_response(ai_response)

    except Exception as e:
        logging.error(f"An error occurred in /chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred: {e}",
        )


# --- SPA (Single Page Application) Routes ---


@app.get("/vite.svg")
def vite_svg():
    return FileResponse(STATIC_DIR / "vite.svg")


@app.get("/manifest.webmanifest")
def manifest():
    return FileResponse(STATIC_DIR / "manifest.webmanifest")


@app.get("/registerSW.js")
def register_sw():
    return FileResponse(STATIC_DIR / "registerSW.js")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.head("/{_path:path}")
def head(_path: str):
    return Response(status_code=200)


@app.get("/{_path:path}")
def spa_fallback(_path: str):
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    setup_logging()
    import uvicorn

    port_str = os.getenv("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        logging.error(
            "Invalid PORT environment variable %r. Falling back to 8000.",
            port_str,
        )
        port = 8000

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
    )
