"""Profile service with DB attempt and in-memory fallback.

Provides simple get/update operations for user profile data.
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

_STORE: Dict[str, Dict] = {}


class ProfileService:
    def __init__(self):
        # In a real deployment this would attempt to use SessionLocal
        # and a persistent `profiles` table. For now, use an in-memory
        # fallback which is sufficient for the UI and tests.
        pass

    def get_profile(self, user_id: str) -> Optional[Dict]:
        try:
            # Attempt DB-backed retrieval if available (optional)
            from server.database import session_scope
            from server import models

            with session_scope() as session:
                # If there were a Profile model, we'd query it here. Fall back
                # to returning an empty profile derived from users table.
                user = (
                    session.query(models.User)
                    .filter(models.User.id == user_id)
                    .one_or_none()
                )
            if user:
                return {
                    "user_id": str(user.id),
                    "email": getattr(user, "email", None),
                    "role": getattr(user, "role", None),
                }
        except Exception:
            logger.exception("Failed to retrieve profile for user %s", user_id)
            # DB not available or model not present; fall back

        return _STORE.get(user_id)

    def update_profile(self, user_id: str, payload: Dict) -> Dict:
        # Merge into store
        existing = _STORE.get(user_id, {})
        existing.update(payload)
        existing["user_id"] = user_id
        _STORE[user_id] = existing
        return existing


profile_service = ProfileService()
