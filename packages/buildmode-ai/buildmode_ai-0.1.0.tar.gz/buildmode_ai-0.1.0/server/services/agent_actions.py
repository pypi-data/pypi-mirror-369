from typing import List, Optional, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import server.database as db
from server import models

router = APIRouter(prefix="/logs/agent-actions", tags=["logs"])


def log_agent_action(
    agent: str,
    action: str,
    sha: Optional[str] = None,
    metadata: Optional[Dict] = None,
) -> None:
    """Persist an AgentActionLog entry."""
    with db.session_scope() as session:
        rec = models.AgentActionLog(
            agent=agent, action=action, sha=sha, metadata_=metadata
        )
        session.add(rec)
        session.commit()


def fetch_agent_actions(db: Session, limit: int = 50) -> List[dict]:
    entries = (
        db.query(models.AgentActionLog)
        .order_by(models.AgentActionLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": e.id,
            "agent": e.agent,
            "action": e.action,
            "sha": e.sha,
            "metadata": e.metadata_,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in entries
    ]


@router.get("")
def get_agent_actions(limit: int = 50, db: Session = Depends(db.get_db)):
    """Return recent agent action log entries."""
    return fetch_agent_actions(db, limit)
