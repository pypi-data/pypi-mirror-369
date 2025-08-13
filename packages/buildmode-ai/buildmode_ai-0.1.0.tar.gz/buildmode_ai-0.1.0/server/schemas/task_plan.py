from pydantic import BaseModel
from typing import List


class TaskPlan(BaseModel):
    task_id: str
    description: str
    status: str  # planned, in-progress, done, failed
    related_files: List[str]
    steps: List[str]
