from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
import uuid

import server.database as db
from server import models

router = APIRouter(prefix="/planner")


class ProjectPlannerAgent:
    def create_tasks_from_description(self, description: str) -> List[str]:
        with db.session_scope() as session:
            tid = str(uuid.uuid4())
            task = models.TaskQueue(
                id=tid,
                title=description,
                description=description,
                status="todo",
            )
            session.add(task)
            session.commit()
            return [tid]


project_planner_agent = ProjectPlannerAgent()


def get_db() -> Session:
    with db.session_scope() as db_session:
        yield db_session


class TaskCreateRequest(BaseModel):
    description: str
    create_plan: bool = False


@router.post("/create-task")
def create_task(req: TaskCreateRequest, db: Session = Depends(get_db)):
    ids = project_planner_agent.create_tasks_from_description(req.description)
    if req.create_plan:
        for tid in ids:
            plan = models.TaskPlanModel(
                task_id=tid,
                description=req.description,
                status="todo",
                related_files=[],
                steps=[],
            )
            db.add(plan)
        db.commit()
    return {"task_ids": ids}


class UpdatePhaseRequest(BaseModel):
    task_id: str
    phase: str


@router.post("/update-phase")
def update_phase(req: UpdatePhaseRequest, db: Session = Depends(get_db)):
    task = db.get(models.TaskQueue, req.task_id)
    if not task:
        return {"status": "not_found"}
    task.phase = req.phase
    db.commit()
    return {"status": "success"}
