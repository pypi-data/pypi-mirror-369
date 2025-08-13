"""Common helper functions for interacting with the database."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Type

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


def create_record(db: Session, model: Type, data: Dict[str, Any]):
    """Create and persist a new database record.

    Args:
        db: Active SQLAlchemy session used for persistence.
        model: ORM model class to instantiate.
        data: Mapping of field names to values for the new record.

    Returns:
        The newly created model instance.
    """
    try:
        record = model(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError:
        db.rollback()
        raise


def get_record(db: Session, model: Type, record_id: Any):
    """Retrieve a single record by its primary key.

    Args:
        db: Active SQLAlchemy session.
        model: ORM model class to query.
        record_id: Primary key value identifying the record.

    Returns:
        The model instance if found, otherwise ``None``.
    """
    return db.get(model, record_id)


def get_all_records(db: Session, model: Type) -> Iterable:
    """Return all records for a given model.

    Args:
        db: Active SQLAlchemy session.
        model: ORM model class to query.

    Returns:
        Iterable of model instances retrieved from the database.
    """
    return db.query(model).all()


def get_user_details(db: Session, user_ids: Iterable[Any]) -> Dict[Any, Any]:
    """Retrieve multiple ``User`` records in a single query.

    Args:
        db: Active SQLAlchemy session.
        user_ids: Iterable of primary key values to fetch.

    Returns:
        Mapping of ``user_id`` to the corresponding ``User`` model instance.

    This implementation uses a single ``SELECT`` with ``WHERE id IN (...)`` so
    that all users are loaded in one round trip.  When additional relationships
    are added to the ``User`` model, SQLAlchemy's eager loading options can be
    supplied here to minimize further query counts.
    """

    from server import models

    ids = list(user_ids)
    if not ids:
        return {}

    stmt = select(models.User).where(models.User.id.in_(ids))
    result = db.execute(stmt).scalars().all()
    return {user.id: user for user in result}


def update_record(db: Session, record: Any, data: Dict[str, Any]):
    """Update an existing record with provided values.

    Args:
        db: Active SQLAlchemy session.
        record: Model instance to modify.
        data: Mapping of fields to updated values.

    Returns:
        The refreshed model instance after commit.
    """
    try:
        for key, value in data.items():
            setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError:
        db.rollback()
        raise


def delete_record(db: Session, record: Any) -> None:
    """Remove a record from the database.

    Args:
        db: Active SQLAlchemy session.
        record: Model instance to delete.

    Returns:
        None
    """
    try:
        db.delete(record)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
