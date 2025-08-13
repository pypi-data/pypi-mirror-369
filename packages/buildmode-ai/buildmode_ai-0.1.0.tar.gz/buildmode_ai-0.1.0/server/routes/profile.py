"""Routes for retrieving and updating user profile information."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict

from server.services.profile_service import profile_service

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfilePayload(BaseModel):
    user_id: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


@router.get("/")
def get_profile(user_id: Optional[str] = None):
    """Return the user's profile or a default stub if it does not exist."""
    uid = user_id or "default-user"
    profile = profile_service.get_profile(uid)
    if not profile:
        # Return a minimal default profile
        return {
            "user_id": uid,
            "display_name": None,
            "bio": None,
            "avatar_url": None,
        }
    return profile


@router.put("/")
def update_profile(payload: ProfilePayload):
    """Update fields on the user's profile and return the new profile."""
    uid = payload.user_id or "default-user"
    data: Dict = payload.dict(exclude_unset=True)
    # remove user_id from payload if present
    data.pop("user_id", None)
    profile = profile_service.update_profile(uid, data)
    return {"status": "ok", "profile": profile}
