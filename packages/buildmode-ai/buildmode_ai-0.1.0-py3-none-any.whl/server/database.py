"""Database session management utilities."""

from contextlib import contextmanager
import logging
import os
import weakref

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from server.config import settings


DATABASE_URL = os.getenv("DATABASE_URL", settings.database_url)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


_active_sessions: "weakref.WeakSet" = weakref.WeakSet()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations.

    Yields:
        Session: Database session object.
    """
    session = SessionLocal()
    _active_sessions.add(session)
    try:
        yield session
    finally:
        session.close()
        _active_sessions.discard(session)


def get_db():
    """Yield a database session that is automatically closed.

    Yields:
        Session: Database session object.
    """
    with session_scope() as db:
        yield db


def active_session_count() -> int:
    """Return the number of active sessions."""
    return len(_active_sessions)


def check_for_connection_leaks(threshold: int = 5) -> int:
    """Warn if active sessions exceed the threshold.

    Args:
        threshold: Active session count that triggers a warning.

    Returns:
        Current active session count.
    """
    count = active_session_count()
    if count > threshold:
        logging.warning("High number of active DB sessions: %d", count)
    return count
