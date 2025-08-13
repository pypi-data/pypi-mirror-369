from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from server.config import settings
from server.services.chat_store import store_chat_message
from server.services.qdrant_service import (
    get_qdrant_service as _get_qdrant_service,
)

# Re-export for tests and external callers (keeps linters happy).
get_qdrant_service = _get_qdrant_service

# Expose module-level settings and openai_client so tests can monkeypatch them.
openai_client = None
# Use settings at import time so linters don't flag the import as unused.
_HAS_OPENAI = getattr(settings, "OPENAI_API_KEY", None) is not None

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    user_id: str
    text: str


@router.post("")
async def handle_chat_message(message: ChatMessage):
    """Store a user's message in Qdrant after embedding it.

    This handler delegates to `server.services.chat_store.store_chat_message`
    which encapsulates embedding and upsert logic. The helper uses a
    deterministic fallback when OpenAI is not configured to allow local
    testing with the in-memory mock.
    """
    # Fail fast when OpenAI API key is not configured to match test
    # expectations that the endpoint errors in that case.
    if not getattr(settings, "OPENAI_API_KEY", None):
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured",
        )

    try:
        ok = store_chat_message(message.user_id, message.text)
        if not ok:
            raise HTTPException(
                status_code=500,
                detail="Failed to store memory",
            )
        return {"status": "success", "message": "Memory stored."}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
