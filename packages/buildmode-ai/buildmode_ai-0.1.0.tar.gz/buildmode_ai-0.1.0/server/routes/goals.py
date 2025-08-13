"""Routes for creating, updating and listing goals."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

import server.database as db
from server import models

router = APIRouter(prefix="/goals", tags=["goals"])


class CreateGoalRequest(BaseModel):
    title: str


class UpdateGoalRequest(BaseModel):
    id: str
    title: Optional[str] = None


@router.post("/create")
def create_goal(request: CreateGoalRequest):
    """Create a new goal and return its identifier."""
    with db.session_scope() as session:
        goal_id = uuid4().hex
        rec = models.Goal(id=goal_id, title=request.title)
        session.add(rec)
        session.commit()
        return {"goal_id": goal_id}


@router.post("/update")
def update_goal(request: UpdateGoalRequest):
    """Update the title of an existing goal."""
    with db.session_scope() as session:
        goal = session.get(models.Goal, request.id)
        if not goal:
            return {"status": "error", "message": "Goal not found"}
        if request.title is not None:
            goal.title = request.title
        session.commit()
        return {"status": "success", "goal_id": request.id}


@router.get("/list")
def list_goals() -> List[dict]:
    """Return all goals ordered by identifier."""
    with db.session_scope() as session:
        goals = session.query(models.Goal).order_by(models.Goal.id).all()
        return [{"id": g.id, "title": g.title} for g in goals]
