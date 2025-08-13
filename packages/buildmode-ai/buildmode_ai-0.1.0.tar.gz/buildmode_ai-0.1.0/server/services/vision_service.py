"""Simple in-memory Vision service for MVP demo purposes.

This is intentionally in-memory to get a working end-to-end flow quickly.
We will migrate to a durable store (Supabase/Postgres) in a later sprint.
"""

from typing import Dict, Optional
import logging

from server.database import session_scope
from server import models

_STORE: Dict[str, Dict[str, str]] = {}


def save_vision(user_id: str, vision: str, anti_vision: str) -> None:
    """Persist vision to DB if possible, otherwise keep in-memory.

    user_id is stored as text (compatible with Supabase user id strings).
    """
    try:
        with session_scope() as session:
            existing = (
                session.query(models.Vision)
                .filter(models.Vision.user_id == user_id)
                .one_or_none()
            )
            if existing:
                existing.vision = vision
                existing.anti_vision = anti_vision
            else:
                v = models.Vision(
                    user_id=user_id,
                    vision=vision,
                    anti_vision=anti_vision,
                )
                session.add(v)
            session.commit()
        return
    except Exception:
        logging.exception("Failed to persist vision for user %s", user_id)
        # fallback to in-memory store
        _STORE[user_id] = {"vision": vision, "anti_vision": anti_vision}


def get_vision(user_id: str) -> Optional[Dict[str, str]]:
    try:
        with session_scope() as session:
            existing = (
                session.query(models.Vision)
                .filter(models.Vision.user_id == user_id)
                .one_or_none()
            )
        if existing:
            return {
                "vision": existing.vision,
                "anti_vision": existing.anti_vision,
            }
    except Exception:
        logging.exception("Failed to retrieve vision for user %s", user_id)
    return _STORE.get(user_id)
