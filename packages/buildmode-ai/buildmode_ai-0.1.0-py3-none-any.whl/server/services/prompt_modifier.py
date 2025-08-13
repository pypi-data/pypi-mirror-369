from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
import yaml

import server.database as db
from server import models
from server.agents.utils import normalize_input

# Directory containing per-agent steering files
CONFIG_DIR = Path("agents/config")

logger = logging.getLogger(__name__)


def _analyze_recent_logs(
    session: Session, since: datetime
) -> Dict[str, Dict[str, int]]:
    """Return aggregated feedback counts per agent."""
    logs = (
        session.query(models.CorrectionLog)
        .filter(models.CorrectionLog.created_at >= since)
        .all()
    )
    updates: Dict[str, Dict[str, int]] = {}
    for log in logs:
        agent = log.agent or "default"
        text = normalize_input(log.human_feedback or "")
        if agent not in updates:
            updates[agent] = {"pr_title_concise": 0}
        if "pr title" in text and "concise" in text:
            updates[agent]["pr_title_concise"] += 1
    return updates


def _update_config(agent: str, counts: Dict[str, int]) -> None:
    """Update the YAML steering file for the given agent."""
    path = CONFIG_DIR / f"{agent}.yaml"
    if path.exists():
        data = yaml.safe_load(path.read_text()) or {}
    else:
        data = {}
    fc = data.get("feedback_counts", {})
    for key, val in counts.items():
        fc[key] = fc.get(key, 0) + val
    data["feedback_counts"] = fc
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def process_corrections(days: int = 1) -> None:
    """Scan recent CorrectionLog entries and update steering files."""
    since = datetime.utcnow() - timedelta(days=days)
    try:
        with db.session_scope() as session:
            updates = _analyze_recent_logs(session, since)
            for agent, counts in updates.items():
                _update_config(agent, counts)
    except Exception:
        logger.exception("prompt modifier failed")
    finally:
        db.check_for_connection_leaks()


_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> BackgroundScheduler:
    """Start the daily APScheduler job."""
    global _scheduler
    if _scheduler is None:
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        _scheduler = BackgroundScheduler()
        trigger = CronTrigger(hour=0, minute=0)
        _scheduler.add_job(process_corrections, trigger)
        _scheduler.start()
        logger.info("Prompt modifier scheduler started")
    return _scheduler
