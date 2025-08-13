from typing import List
from fastapi import APIRouter

router = APIRouter(tags=["phases"])


PHASES: List[str] = ["todo", "in-progress", "review", "done"]


@router.get("/phases")
def list_phases() -> List[str]:
    """Return the available task phases."""
    return PHASES
