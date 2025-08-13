"""Store chat messages as vector points in Qdrant."""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List

from server.agents.utils import normalize_input
from .qdrant_service import get_qdrant_service

LOG = logging.getLogger("server.services.chat_store")
LOG.propagate = True

# Tests expect this collection name.
COLLECTION_NAME = "user_memories"


def _local_embedding(text: str) -> List[float]:
    """Tiny deterministic embedding used in tests/offline."""
    h = sum(ord(c) for c in text)
    return [(h % 97) / 97.0, ((h // 7) % 101) / 101.0]


def _get_embedding(text: str) -> List[float]:
    """Get an embedding; avoid network in tests/CI."""
    env = normalize_input(os.getenv("NODE_ENV", ""))
    if env in {"test", "ci"}:
        return _local_embedding(text)

    key = os.getenv("OPENAI_API_KEY") or ""
    if not key:
        return _local_embedding(text)

    try:
        # Optional dependency; if missing or failing, we fall back.
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=key)
        resp = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        data = getattr(resp, "data", [])
        if data:
            emb = getattr(data[0], "embedding", None)
            if emb:
                return list(emb)
    except Exception as e:  # pragma: no cover
        LOG.warning("Embedding fetch failed, using local: %s", e)

    return _local_embedding(text)


def store_chat_message(user_id: str, text: str) -> bool:
    """Compute an embedding and upsert a point into Qdrant."""
    svc = get_qdrant_service()
    vector = _get_embedding(text)

    point: Dict[str, Any] = {
        "id": f"{user_id}:{int(time.time() * 1000)}",
        "vector": list(vector),
        "payload": {
            "user_id": user_id,
            "text": text,
            "timestamp": int(time.time()),
        },
    }
    return bool(svc.upsert_points(COLLECTION_NAME, [point]))
