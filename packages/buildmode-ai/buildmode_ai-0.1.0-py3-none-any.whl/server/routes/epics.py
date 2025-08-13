"""Routes for creating, updating, and listing epics."""

from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

import server.database as db
from server import models

router = APIRouter(prefix="/epics", tags=["epics"])


# --------- Schemas ---------
class CreateEpicRequest(BaseModel):
    title: str
    goal_id: Optional[str] = None


class UpdateEpicRequest(BaseModel):
    id: str
    title: Optional[str] = None
    goal_id: Optional[str] = None


class EpicOut(BaseModel):
    id: str
    title: str
    goal_id: Optional[str] = None


class CreateEpicResponse(BaseModel):
    epic_id: str


# --------- Routes ---------
@router.post(
    "/create",
    response_model=CreateEpicResponse,
    status_code=status.HTTP_200_OK,
)
def create_epic(request: CreateEpicRequest) -> CreateEpicResponse:
    """Create a new epic optionally linked to a goal."""
    with db.session_scope() as session:
        epic_id = uuid4().hex
        rec = models.Epic(
            id=epic_id,
            title=request.title,
            goal_id=request.goal_id,
        )
        session.add(rec)
        session.commit()
        return CreateEpicResponse(epic_id=epic_id)


@router.post("/update")
def update_epic(request: UpdateEpicRequest):
    """Update an epic's attributes such as title or goal association."""
    with db.session_scope() as session:
        epic = session.get(models.Epic, request.id)
        if not epic:
            raise HTTPException(status_code=404, detail="Epic not found")

        # Update only fields the client actually sent
        payload = request.model_dump(exclude_unset=True, exclude={"id"})
        for field, value in payload.items():
            setattr(epic, field, value)

        session.commit()
        return {"status": "success", "epic_id": request.id}


@router.get("/list", response_model=List[EpicOut])
def list_epics() -> List[EpicOut]:
    """Return all epics ordered by identifier."""
    with db.session_scope() as session:
        epics = session.query(models.Epic).order_by(models.Epic.id).all()
        return [
            EpicOut(id=e.id, title=e.title, goal_id=e.goal_id) for e in epics
        ]
