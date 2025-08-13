from fastapi import APIRouter, Request
import re

import server.database as db
from server import models

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _extract_task_id(text: str) -> str | None:
    patterns = [
        # Allow variations like "task-id=123" or "task_id: '123'"
        r"task[_-]?id[:= ]*['\"]?([a-fA-F0-9-]+)['\"]?",
        # Match shorthand markers such as "[task:123]"
        r"\[task:([a-fA-F0-9-]+)\]",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


@router.post("/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    event = request.headers.get("X-GitHub-Event")
    payload = await request.json()

    if event != "pull_request":
        return {"status": "ignored"}

    action = payload.get("action")
    pr = payload.get("pull_request", {})

    if action == "closed" and pr.get("merged"):
        title = pr.get("title", "")
        body = pr.get("body", "")
        task_id = _extract_task_id(title) or _extract_task_id(body)
        if task_id:
            base_ref = pr.get("base", {}).get("ref", "")
            new_status = "done" if base_ref == "main" else "review"
            with db.session_scope() as session:
                task = session.get(models.TaskQueue, task_id)
                if task:
                    task.status = new_status
                    session.commit()
    return {"status": "ok"}
