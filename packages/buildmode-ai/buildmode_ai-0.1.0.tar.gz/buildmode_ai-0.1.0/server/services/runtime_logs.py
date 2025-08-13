import json  # for structured log parsing
import logging
from typing import Optional, Tuple, List
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import server.database as db
from server import models

try:
    from google.cloud import logging_v2  # pragma: no cover - optional
except Exception:  # pragma: no cover
    logging_v2 = None

router = APIRouter(prefix="/logs", tags=["logs"])


def parse_log_line(line: str) -> Optional[Tuple[datetime, str, str, str]]:
    """Parse a structured runtime log line encoded as JSON."""
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None

    ts_str = data.get("timestamp") or data.get("time")
    timestamp = None
    if ts_str:
        try:
            if ts_str.endswith("Z"):
                ts_str = ts_str.replace("Z", "+00:00")  # Support UTC shorthand
            timestamp = datetime.fromisoformat(ts_str)
        except Exception:
            timestamp = None
    level = data.get("severity") or data.get("level")
    service = (
        data.get("service")
        or data.get("serviceName")
        or data.get("resource", {}).get("labels", {}).get("service_name")
    )  # Explore typical Cloud Run fields for service name
    message = (
        data.get("message")
        or data.get("textPayload")
        or data.get("jsonPayload", {}).get("message")
    )  # Handle multiple log message locations
    if timestamp and level and message:
        return timestamp, service or "unknown", level, message
    return None


def ingest_log_line(line: str) -> bool:
    """Parse and store a single log line if it's an error."""
    parsed = parse_log_line(line)
    if not parsed:
        return False

    ts, service, level, message = parsed
    if level.upper() not in {"ERROR", "CRITICAL"}:
        return False

    with db.session_scope() as session:
        try:
            rec = models.RuntimeLog(
                timestamp=ts, service=service, level=level, message=message
            )
            session.add(rec)
            session.commit()
            return True
        except Exception:
            session.rollback()
            logging.exception("Failed to store runtime log")
            return False


def fetch_recent_logs(db: Session, limit: int = 50) -> List[dict]:
    entries = (
        db.query(models.RuntimeLog)
        .order_by(models.RuntimeLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "service": e.service,
            "level": e.level,
            "message": e.message,
        }
        for e in entries
    ]


@router.get("/recent")
def get_recent_logs(limit: int = 50, db: Session = Depends(db.get_db)):
    """Return recently ingested runtime logs."""
    return fetch_recent_logs(db, limit)


def stream_runtime_logs(service_name: str, level: str = "ERROR") -> None:
    """Background task that pulls runtime logs and stores errors."""
    if logging_v2 is None:
        raise RuntimeError("google-cloud-logging is not installed")

    client = logging_v2.Client()
    flt = (
        'resource.type="cloud_run_revision" '
        f'resource.labels.service_name="{service_name}" severity>={level}'
    )
    for entry in client.list_entries(filter_=flt):
        ingest_log_line(json.dumps(entry.to_api_repr()))
