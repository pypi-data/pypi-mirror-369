from __future__ import annotations

from sqlalchemy.orm import Session

import server.database as db


class BaseAgent:
    """Common utilities shared by agent helpers."""

    def __init__(self) -> None:
        self._session_ctx = None
        self.db: Session | None = None

    def close(self) -> None:
        if getattr(self, "_session_ctx", None):
            self._session_ctx.__exit__(None, None, None)
            self._session_ctx = None
            self.db = None

    # Context manager support
    def __enter__(self) -> "BaseAgent":
        self._session_ctx = db.session_scope()
        self.db = self._session_ctx.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if getattr(self, "_session_ctx", None):
            self._session_ctx.__exit__(exc_type, exc, tb)
            self._session_ctx = None
            self.db = None
