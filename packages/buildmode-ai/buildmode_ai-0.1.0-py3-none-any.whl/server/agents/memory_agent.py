"""Memory agent: embed text and persist to Qdrant via QdrantService.

This agent demonstrates how an agent can obtain embeddings and upsert
memory vectors into the `user_memories` collection. The implementation is
kept deliberately simple and uses a pluggable embedding helper so tests
can patch it and avoid external network calls.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List

from server.agents.base import BaseAgent
from server.services.qdrant_service import get_qdrant_service


def _get_embedding(text: str) -> List[float]:
    """Return an embedding for `text`.

    This default implementation returns a small deterministic vector for
    local development and tests. Production code should replace this with
    a call to a real embedding provider.
    """
    # Use a tiny deterministic fallback to avoid network calls in tests.
    # Tests can monkeypatch `server.agents.memory_agent._get_embedding`
    # to return specific vectors when needed.
    return [float((ord(c) % 10) / 10.0) for c in (text or "")[:3]] or [
        0.1,
        0.1,
        0.1,
    ]


class MemoryAgent(BaseAgent):
    """Agent that stores a user's message as a memory vector in Qdrant.

    Input payload: {"user_id": str, "text": str}
    Returns: dict with status and optional details.
    """

    COLLECTION = "user_memories"

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        user_id = payload.get("user_id")
        text = payload.get("text")
        if not user_id or not text:
            return {"status": "error", "message": "user_id and text required"}

        vector = _get_embedding(text)

        service = get_qdrant_service()
        # Build a simple point structure the QdrantService understands.
        point = {
            "id": f"{user_id}:{uuid.uuid4().hex}",
            "vector": vector,
            "payload": {"user_id": user_id, "text": text},
        }

        ok = service.upsert_points(self.COLLECTION, [point])
        if not ok:
            return {"status": "error", "message": "failed to upsert points"}
        return {"status": "success", "point_id": point["id"]}
