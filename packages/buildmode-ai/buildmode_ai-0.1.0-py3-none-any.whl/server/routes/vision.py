"""Routes for storing and retrieving a user's vision statements."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from server.services.vision_service import save_vision, get_vision

router = APIRouter(prefix="/vision", tags=["vision"])


class VisionPayload(BaseModel):
    user_id: Optional[str] = None
    vision: str
    anti_vision: str


@router.post("/")
def post_vision(payload: VisionPayload):
    """Persist a user's vision and anti-vision.

    Return the user identifier.
    """
    uid = payload.user_id or "default-user"
    save_vision(uid, payload.vision, payload.anti_vision)
    return {"status": "ok", "user_id": uid}


@router.get("/")
def read_vision(user_id: Optional[str] = None):
    """Retrieve the stored vision for a user or raise 404 if missing."""
    uid = user_id or "default-user"
    v = get_vision(uid)
    if not v:
        raise HTTPException(status_code=404, detail="Vision not found")
    return v
