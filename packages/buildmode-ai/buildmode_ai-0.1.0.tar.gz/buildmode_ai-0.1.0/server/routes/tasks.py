"""Routes for creating, updating and tracking tasks and comments."""

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import func
from server import models
import server.database as db

router = APIRouter(prefix="/tasks", tags=["tasks"])
logger = logging.getLogger(__name__)


def get_db():
    with db.session_scope() as session:
        yield session


class TaskWSManager:
    """Manage WebSocket connections for task updates."""

    def __init__(self) -> None:
        self.connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.connections.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.connections:
            self.connections.remove(ws)

    async def broadcast(self, message: Dict[str, str]) -> None:
        to_remove: List[WebSocket] = []
        for ws in list(self.connections):
            try:
                await ws.send_json(message)
            except Exception:
                logger.exception("Error sending message to WebSocket")
                to_remove.append(ws)
        for ws in to_remove:
            self.disconnect(ws)


ws_manager = TaskWSManager()


class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int = 0
    phase: str = "todo"
    status: str = "open"
    task_type: str = "general"
    assignee: Optional[str] = None
    parent_id: Optional[str] = None
    epic_id: Optional[str] = None


class UpdateTaskRequest(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    phase: Optional[str] = None
    status: Optional[str] = None
    task_type: Optional[str] = None
    assignee: Optional[str] = None
    parent_id: Optional[str] = None
    epic_id: Optional[str] = None


class CommentRequest(BaseModel):
    comment: str
    author: Optional[str] = "system"


class OverrideRequest(BaseModel):
    task_id: str
    label: str


@router.post("/create")
async def create_task(
    request: CreateTaskRequest,
    db: Session = Depends(get_db),
):
    """Create a task in the queue and notify WebSocket listeners."""
    task_id = uuid4().hex
    record = models.TaskQueue(
        id=task_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        phase=request.phase,
        status=request.status,
        task_type=request.task_type,
        assignee=request.assignee,
        parent_id=request.parent_id,
        epic_id=request.epic_id,
    )
    db.add(record)
    db.commit()
    await ws_manager.broadcast({"event": "created", "task_id": task_id})
    return {"task_id": task_id}


@router.post("/update")
async def update_task(
    request: UpdateTaskRequest,
    db: Session = Depends(get_db),
):
    """Update an existing task with new values and broadcast the change."""
    task = db.get(models.TaskQueue, request.id)
    if not task:
        return {"status": "error", "message": "Task not found"}
    for field, value in request.model_dump(exclude_unset=True).items():
        if field == "id":
            continue
        setattr(task, field, value)
    db.commit()
    await ws_manager.broadcast({"event": "updated", "task_id": request.id})
    return {"status": "success", "task_id": request.id}


@router.get("/list")
def list_tasks(db: Session = Depends(get_db)) -> List[dict]:
    """Return all tasks ordered by creation time."""
    tasks = (
        db.query(models.TaskQueue)
        .order_by(models.TaskQueue.created_at.asc())
        .all()
    )
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "phase": t.phase,
            "status": t.status,
            "task_type": t.task_type,
            "assignee": t.assignee,
            "parent_id": t.parent_id,
            "epic_id": t.epic_id,
            "created_at": (t.created_at.isoformat() if t.created_at else None),
            "updated_at": (t.updated_at.isoformat() if t.updated_at else None),
        }
        for t in tasks
    ]


@router.get("/next")
def next_task(db: Session = Depends(get_db)):
    """Return the highest priority task that is not marked done."""
    task = (
        db.query(models.TaskQueue)
        .filter(models.TaskQueue.status != "done")
        .order_by(
            models.TaskQueue.priority.desc(), models.TaskQueue.created_at.asc()
        )
        .first()
    )
    if not task:
        return {}
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "phase": task.phase,
        "status": task.status,
        "task_type": task.task_type,
        "assignee": task.assignee,
        "parent_id": task.parent_id,
        "epic_id": task.epic_id,
        "created_at": (
            task.created_at.isoformat() if task.created_at else None
        ),
        "updated_at": (
            task.updated_at.isoformat() if task.updated_at else None
        ),
    }


@router.post("/{task_id}/comments")
async def add_comment(
    task_id: str,
    request: CommentRequest,
    db: Session = Depends(get_db),
):
    """Add a comment to a task and broadcast the new comment."""
    comment = models.TaskComment(
        task_id=task_id, comment=request.comment, author=request.author
    )
    db.add(comment)
    db.commit()
    await ws_manager.broadcast({"event": "comment", "task_id": task_id})
    return {"id": comment.id}


@router.get("/{task_id}/comments")
def list_comments(task_id: str, db: Session = Depends(get_db)) -> List[dict]:
    """List all comments for a task ordered by creation time."""
    comments = (
        db.query(models.TaskComment)
        .filter(models.TaskComment.task_id == task_id)
        .order_by(models.TaskComment.created_at.asc())
        .all()
    )
    return [
        {
            "id": c.id,
            "task_id": c.task_id,
            "comment": c.comment,
            "author": c.author,
            "created_at": (c.created_at.isoformat() if c.created_at else None),
        }
        for c in comments
    ]


@router.post("/override")
async def override_task(
    request: OverrideRequest,
    db: Session = Depends(get_db),
):
    """Reset a task's status when an override label is provided."""
    if request.label != "#override":
        return {"status": "error", "message": "Invalid label"}
    try:
        with db.begin():
            task = db.get(models.TaskQueue, request.task_id)
            if not task:
                raise LookupError("Task not found")
            task.status = "open"
            db.add(
                models.TaskComment(
                    task_id=task.id, comment=request.label, author="human"
                )
            )
            db.add(
                models.AgentActionLog(
                    agent="tasks",
                    action="override",
                    sha=None,
                    metadata_={"task_id": task.id},
                )
            )
    except LookupError:
        return {"status": "error", "message": "Task not found"}
    except Exception:
        logger.exception("Failed to override task")
        return {"status": "error", "message": "Override failed"}
    await ws_manager.broadcast({"event": "override", "task_id": task.id})
    return {"status": "success"}


@router.get("/status")
def tasks_status(db: Session = Depends(get_db)) -> dict:
    """Return counts of tasks grouped by status."""
    rows = (
        db.query(models.TaskQueue.status, func.count())
        .group_by(models.TaskQueue.status)
        .all()
    )
    counts = {status: count for status, count in rows}
    return {"total": int(sum(counts.values())), "by_status": counts}


@router.get("/log")
def task_log(limit: int = 20, db: Session = Depends(get_db)) -> List[dict]:
    """Return recent task comments as log entries."""
    comments = (
        db.query(models.TaskComment)
        .order_by(models.TaskComment.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": c.id,
            "task_id": c.task_id,
            "comment": c.comment,
            "author": c.author,
            "created_at": (c.created_at.isoformat() if c.created_at else None),
        }
        for c in comments
    ]


async def tasks_ws(websocket: WebSocket):
    """Maintain a WebSocket connection for task update events."""
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
