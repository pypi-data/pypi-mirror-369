import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import or_, bindparam
from sqlalchemy.exc import SQLAlchemyError

import server.database as db
from server import models
from server.schemas.memory_entry import MemoryEntry as MemoryEntrySchema
from server.memory_graph import add_entry, get_connections
from server.services.qdrant_service import get_qdrant_service

memory_router = APIRouter(prefix="/memory", tags=["memory"])


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_memory_entry(path: str) -> Optional[Dict[str, Any]]:
    """Retrieve a memory entry by file path."""
    with db.session_scope() as session:
        entry = (
            session.query(models.MemoryEntry)
            .filter(models.MemoryEntry.file_path == path)
            .first()
        )
        if entry:
            return {
                "file_path": entry.file_path,
                "summary": entry.summary,
                "full_text": entry.full_text,
                "notes": entry.notes,
            }
    return None


def store_memory_entry(entry: MemoryEntrySchema) -> Dict[str, Any]:
    """Create or update a memory entry."""
    with db.session_scope() as session:
        obj = (
            session.query(models.MemoryEntry)
            .filter(models.MemoryEntry.file_path == entry.file_path)
            .first()
        )
        if obj:
            obj.summary = entry.summary
            obj.full_text = entry.full_text
            obj.notes = entry.notes
        else:
            obj = models.MemoryEntry(**entry.model_dump())
            session.add(obj)
        session.commit()
    add_entry(entry.file_path)
    return {"status": "success"}


def write_file_memory(
    file_path: str,
    summary: Optional[str] = None,
    functions: Optional[List[str]] = None,
    components: Optional[List[str]] = None,
    api_routes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Store metadata about a code file."""
    with db.session_scope() as session:
        obj = (
            session.query(models.MemoryFile)
            .filter(models.MemoryFile.file_path == file_path)
            .first()
        )
        data = {
            "file_path": file_path,
            "summary": summary,
            "functions": functions or [],
            "components": components or [],
            "api_routes": api_routes or [],
        }
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = models.MemoryFile(**data)
            session.add(obj)
        session.commit()
    add_entry(file_path)
    return {"status": "success", "file_path": file_path}


def search_memory(keyword: str) -> List[Dict[str, Any]]:
    """Search memory entries for a keyword."""
    with db.session_scope() as session:
        pattern = f"%{keyword}%"
        kw = bindparam("kw")
        results = (
            session.query(models.MemoryEntry)
            .filter(
                or_(
                    models.MemoryEntry.summary.ilike(kw),
                    models.MemoryEntry.full_text.ilike(kw),
                    models.MemoryEntry.notes.ilike(kw),
                )
            )
            .params(kw=pattern)
            .all()
        )
        return [
            {
                "file_path": r.file_path,
                "summary": r.summary,
                "full_text": r.full_text,
                "notes": r.notes,
            }
            for r in results
        ]


def query_memory(query: str) -> Dict[str, Any]:
    """Query both memory entries and code file metadata."""
    with db.session_scope() as session:
        pattern = f"%{query}%"
        kw = bindparam("kw")
        entry_results = (
            session.query(models.MemoryEntry)
            .filter(
                or_(
                    models.MemoryEntry.file_path.ilike(kw),
                    models.MemoryEntry.summary.ilike(kw),
                    models.MemoryEntry.full_text.ilike(kw),
                    models.MemoryEntry.notes.ilike(kw),
                )
            )
            .params(kw=pattern)
            .all()
        )
        file_results = (
            session.query(models.MemoryFile)
            .filter(
                or_(
                    models.MemoryFile.summary.ilike(kw),
                    models.MemoryFile.file_path.ilike(kw),
                )
            )
            .params(kw=pattern)
            .all()
        )
        return {
            "entries": [
                {
                    "file_path": e.file_path,
                    "summary": e.summary,
                    "full_text": e.full_text,
                    "notes": e.notes,
                }
                for e in entry_results
            ],
            "files": [
                {
                    "file_path": f.file_path,
                    "summary": f.summary,
                    "functions": f.functions,
                    "components": f.components,
                    "api_routes": f.api_routes,
                }
                for f in file_results
            ],
        }


def search_memory_vectors(
    query: str, collection_name: str = "memory_files", limit: int = 10
) -> List[Dict[str, Any]]:
    """Search stored vectors for entries semantically similar to ``query``.

    Intended behaviour:

    * Embed the provided ``query`` text using the application's embedding
      strategy.
    * Perform a vector similarity search against the ``collection_name``
      collection in Qdrant and return up to ``limit`` matches ordered by
      relevance.

    The vector store integration has not been implemented yet; calling this
    function will therefore raise :class:`NotImplementedError` to make the
    limitation explicit.
    """
    raise NotImplementedError("Vector search is not implemented")


def hybrid_search_memory(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Combine keyword and vector search over memory entries.

    The expected implementation would blend traditional keyword matching with
    vector similarity search results, returning the most relevant documents. At
    present this behaviour is unavailable and the function simply signals this
    by raising :class:`NotImplementedError`.
    """
    raise NotImplementedError("Hybrid search is not implemented")


def upsert_memory_vector(
    file_path: str,
    content: Optional[str] = None,
    collection_name: str = "memory_files",
) -> bool:
    """Create or update the vector representation of a file in Qdrant.

    A full implementation would embed ``content`` (or retrieve it from
    ``file_path``), then upsert the resulting vector into the specified
    ``collection_name`` using :mod:`qdrant_service`.

    Currently the application does not support this functionality, so calling
    the function raises :class:`NotImplementedError`.
    """
    raise NotImplementedError("Vector upsert is not implemented")


def store_build_log(
    build_id: str, log_content: str, metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Persist a build log entry."""
    with db.session_scope() as session:
        log = models.BuildLog(
            build_id=build_id,
            log_content=log_content,
            metadata_=metadata or {},
        )
        session.add(log)
        session.commit()
        session.refresh(log)
        return {"id": log.id, "build_id": build_id}


def get_build_log(build_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a build log by build identifier."""
    with db.session_scope() as session:
        log = (
            session.query(models.BuildLog)
            .filter(models.BuildLog.build_id == build_id)
            .order_by(models.BuildLog.created_at.desc())
            .first()
        )
        if log:
            return {
                "id": log.id,
                "build_id": log.build_id,
                "log_content": log.log_content,
                "metadata": log.metadata_,
            }
    return None


def store_prompt_feedback(
    task_id: str,
    original_prompt: str,
    updated_prompt: str,
    correction: Optional[str] = None,
) -> Dict[str, Any]:
    """Store prompt correction feedback."""
    with db.session_scope() as session:
        fb = models.PromptFeedback(
            task_id=task_id,
            original_prompt=original_prompt,
            updated_prompt=updated_prompt,
            correction=correction,
        )
        session.add(fb)
        session.commit()
        session.refresh(fb)
        return {"id": fb.id}


def get_prompt_feedback(task_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve prompt feedback entries for a task."""
    with db.session_scope() as session:
        items = (
            session.query(models.PromptFeedback)
            .filter(models.PromptFeedback.task_id == task_id)
            .order_by(models.PromptFeedback.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": i.id,
                "task_id": i.task_id,
                "original_prompt": i.original_prompt,
                "updated_prompt": i.updated_prompt,
                "correction": i.correction,
            }
            for i in items
        ]


def store_correction_log(
    task_id: str,
    agent: Optional[str] = None,
    outcome: Optional[str] = None,
    human_feedback: Optional[str] = None,
) -> Dict[str, Any]:
    """Store a correction log entry."""
    with db.session_scope() as session:
        log = models.CorrectionLog(
            task_id=task_id,
            agent=agent or "",
            outcome=outcome,
            human_feedback=human_feedback,
        )
        session.add(log)
        session.commit()
        session.refresh(log)
        return {"id": log.id}


def get_correction_logs(task_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve correction log entries."""
    with db.session_scope() as session:
        logs = (
            session.query(models.CorrectionLog)
            .filter(models.CorrectionLog.task_id == task_id)
            .order_by(models.CorrectionLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": log_entry.id,
                "task_id": log_entry.task_id,
                "agent": log_entry.agent,
                "outcome": log_entry.outcome,
                "human_feedback": log_entry.human_feedback,
            }
            for log_entry in logs
        ]


def list_memory_entries() -> List[Dict[str, Any]]:
    with db.session_scope() as session:
        try:
            entries = session.query(models.MemoryEntry).all()
        except SQLAlchemyError:
            return []
        return [
            {
                "file_path": e.file_path,
                "summary": e.summary,
                "full_text": e.full_text,
                "notes": e.notes,
            }
            for e in entries
        ]


# ---------------------------------------------------------------------------
# Router endpoints
# ---------------------------------------------------------------------------


@memory_router.get("/")
def list_memory() -> Dict[str, Any]:
    return {"entries": list_memory_entries()}


@memory_router.get("/get")
def read_memory(path: str) -> Dict[str, Any]:
    entry = get_memory_entry(path)
    if not entry:
        raise HTTPException(status_code=404, detail="Memory entry not found")
    return entry


@memory_router.post("/store")
def store_memory(entry: MemoryEntrySchema) -> Dict[str, Any]:
    return store_memory_entry(entry)


@memory_router.post("/file")
def store_file_memory(payload: Dict[str, Any]) -> Dict[str, Any]:
    file_path = payload.get("file_path")
    if not file_path:
        raise HTTPException(status_code=400, detail="file_path required")
    return write_file_memory(
        file_path,
        summary=payload.get("summary"),
        functions=payload.get("functions"),
        components=payload.get("components"),
        api_routes=payload.get("api_routes"),
    )


@memory_router.get("/search")
def search_memory_endpoint(keyword: str) -> Dict[str, Any]:
    return {"results": search_memory(keyword)}


@memory_router.get("/query")
def query_memory_endpoint(query: str) -> StreamingResponse:
    result = json.dumps(query_memory(query))
    return StreamingResponse(iter([result]), media_type="application/json")


@memory_router.get("/graph")
def get_graph(file_path: str) -> Dict[str, Any]:
    data = get_connections(file_path)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return data


@memory_router.get("/search/vector")
def search_vector_endpoint(
    query: str, collection: str = "memory_files", limit: int = 10
) -> Dict[str, Any]:
    return {"results": search_memory_vectors(query, collection, limit)}


@memory_router.get("/search/hybrid")
def search_hybrid_endpoint(query: str, limit: int = 10) -> Dict[str, Any]:
    return {"results": hybrid_search_memory(query, limit)}


@memory_router.post("/qdrant/upsert")
def qdrant_upsert_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    file_path = payload.get("file_path")
    if not file_path:
        raise HTTPException(status_code=400, detail="file_path required")
    success = upsert_memory_vector(file_path, payload.get("content"))
    if success:
        return {"status": "success"}
    raise HTTPException(status_code=500, detail="Vector upsert failed")


@memory_router.get("/qdrant/health")
def qdrant_health_endpoint() -> Dict[str, Any]:
    service = get_qdrant_service()
    return service.health_check()


@memory_router.get("/qdrant/collections")
def qdrant_collections_endpoint() -> Dict[str, Any]:
    service = get_qdrant_service()
    if not service.client:
        return {"error": "Qdrant client not initialized"}
    try:
        cols = service.client.get_collections()
        infos = []
        for col in cols.collections:
            info = service.get_collection_info(col.name)
            infos.append(info or {"name": col.name})
        return {"collections": infos}
    except Exception as e:  # pragma: no cover - network dependent
        return {"error": str(e)}


@memory_router.post("/build-log")
def store_build_log_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    build_id = payload.get("build_id")
    log_content = payload.get("log_content")
    if not build_id or not log_content:
        raise HTTPException(
            status_code=400, detail="build_id and log_content required"
        )
    store_build_log(build_id, log_content, payload.get("metadata"))
    return {"status": "success"}


@memory_router.get("/build-log")
def get_build_log_endpoint(build_id: str) -> Dict[str, Any]:
    log = get_build_log(build_id)
    if not log:
        raise HTTPException(status_code=404, detail="Build log not found")
    return log


@memory_router.post("/prompt-feedback")
def store_prompt_feedback_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    task_id = payload.get("task_id")
    original_prompt = payload.get("original_prompt")
    updated_prompt = payload.get("updated_prompt")
    correction = payload.get("correction")
    if not task_id or not original_prompt or not updated_prompt:
        raise HTTPException(
            status_code=400,
            detail="task_id, original_prompt and updated_prompt required",
        )
    store_prompt_feedback(task_id, original_prompt, updated_prompt, correction)
    return {"status": "success"}


@memory_router.get("/prompt-feedback")
def get_prompt_feedback_endpoint(
    task_id: str, limit: int = 20
) -> Dict[str, Any]:
    return {"feedback": get_prompt_feedback(task_id, limit)}


@memory_router.post("/corrections")
def store_correction_log_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    task_id = payload.get("task_id")
    agent = payload.get("agent")
    outcome = payload.get("outcome")
    human_feedback = payload.get("human_feedback")
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id required")
    store_correction_log(task_id, agent, outcome, human_feedback)
    return {"status": "success"}


@memory_router.get("/corrections")
def get_corrections_endpoint(task_id: str, limit: int = 20) -> Dict[str, Any]:
    return {"corrections": get_correction_logs(task_id, limit)}
