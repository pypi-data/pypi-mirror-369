"""Qdrant service wrapper, in‑memory mock, and a retry helper."""

from __future__ import annotations

import logging
import math
import os
import time
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

from server.agents.utils import normalize_input

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

LOGGER_NAME = "server.services.qdrant_service"

# Ensure pytest's caplog can always capture our records
_LOGGER_BOOT = logging.getLogger(LOGGER_NAME)
_LOGGER_BOOT.propagate = True
_LOGGER_BOOT.disabled = False


def _lg() -> logging.Logger:
    """Return module logger and ensure it can propagate to caplog."""
    lg = logging.getLogger(LOGGER_NAME)
    if not getattr(lg, "propagate", True):
        lg.propagate = True
    if getattr(lg, "disabled", False):
        lg.disabled = False
    return lg


try:
    # Patched by tests as server.services.qdrant_service.QdrantClient
    from qdrant_client import QdrantClient  # type: ignore
except Exception:  # pragma: no cover
    QdrantClient = None  # type: ignore


# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------


def _retry(
    func,
    attempts: int = 3,
    backoff: float = 0.5,
    exceptions: Tuple[type[Exception], ...] = (Exception,),
):
    """Retry wrapper with DEBUG logs and ERROR on exhaustion."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    def wrapper(*args, **kwargs):
        last_exc: Optional[Exception] = None
        for i in range(attempts):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exc = e
                _lg().debug("Attempt %d/%d failed: %s", i + 1, attempts, e)
                if i < attempts - 1:
                    sleep_for = backoff * (2**i)
                    time.sleep(sleep_for)
                else:
                    op = getattr(func, "__name__", "operation")
                    _lg().error(
                        "Operation %s failed after %d attempts", op, attempts
                    )
                    raise
        raise last_exc if last_exc else RuntimeError("retry failed")

    return wrapper


# ---------------------------------------------------------------------------
# Qdrant mock
# ---------------------------------------------------------------------------


class QdrantMock:
    """In‑memory mock. Stores points as dicts for test convenience."""

    def __init__(self) -> None:
        # _cols: collection -> list of dict points
        self._cols: Dict[str, List[Dict[str, Any]]] = {}

    def create_collection(
        self, collection_name: str, *args: Any, **kwargs: Any
    ) -> bool:
        if collection_name not in self._cols:
            self._cols[collection_name] = []
        return True

    def delete_collection(self, name: str) -> bool:
        if name in self._cols:
            del self._cols[name]
        return True

    def get_collections(self) -> SimpleNamespace:
        cols = [SimpleNamespace(name=n) for n in sorted(self._cols.keys())]
        return SimpleNamespace(collections=cols)

    def get_collection(self, name: str) -> SimpleNamespace:
        pts = self._cols.get(name, [])
        return SimpleNamespace(
            vectors_count=len(pts),
            indexed_vectors_count=len(pts),
            points_count=len(pts),
            status="green",
        )

    def upsert(
        self,
        collection_name: Optional[str] = None,
        points: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> bool:
        if collection_name is None:
            collection_name = kwargs.get("collection_name")
        if points is None:
            points = kwargs.get("points")
        if collection_name is None or points is None:
            raise TypeError("upsert needs collection_name and points")
        self.create_collection(collection_name)
        bucket = self._cols[collection_name]
        idx_by_id = {p.get("id"): i for i, p in enumerate(bucket)}
        for p in points:
            pid = p.get("id")
            # Accept multiple key names
            vec = p.get("vector") or p.get("embedding") or []
            pl = p.get("payload") or {}
            # Normalize point structure
            point = {
                "id": pid,
                "vector": list(vec),
                "payload": dict(pl),
            }
            if pid in idx_by_id:
                bucket[idx_by_id[pid]] = point
            else:
                bucket.append(point)
        return True

    def search(
        self,
        collection_name: Optional[str] = None,
        query_vector: Optional[List[float]] = None,
        limit: int = 10,
        with_payload: bool = True,
        **kwargs: Any,
    ) -> List[SimpleNamespace]:
        if collection_name is None:
            collection_name = kwargs.get("collection_name")
        if query_vector is None:
            query_vector = kwargs.get("query_vector")
        if collection_name is None:
            raise TypeError("search needs collection_name")
        pts = self._cols.get(collection_name, [])

        def make_obj(p: Dict[str, Any], sc: float) -> SimpleNamespace:
            return SimpleNamespace(
                id=p.get("id"),
                vector=list(p.get("vector") or []),
                payload=dict(p.get("payload") or {}),
                score=sc,
            )

        if query_vector is None:
            out = [make_obj(p, 0.0) for p in pts[:limit]]
            return out

        def score(vec: List[float]) -> float:
            if not vec or not query_vector:
                return 0.0
            dot = sum(a * b for a, b in zip(vec, query_vector))
            na = math.sqrt(sum(a * a for a in vec))
            nb = math.sqrt(sum(b * b for b in query_vector))
            if not na or not nb:
                return 0.0
            return dot / (na * nb)  # Cosine similarity

        scored = [make_obj(p, score(p.get("vector") or [])) for p in pts]
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:limit]


# ---------------------------------------------------------------------------
# Qdrant service
# ---------------------------------------------------------------------------


def _is_unittest_mock(obj: Any) -> bool:
    mod = getattr(obj, "__module__", "")
    return mod.startswith("unittest.mock") or mod.endswith(".mock")


class QdrantService:
    """Minimal wrapper used by the app."""

    def __init__(self) -> None:
        self.host = os.getenv("QDRANT_HOST", "buildmode-qdrant")
        port_str = os.getenv("QDRANT_PORT", "6333")
        try:
            self.port = int(port_str)
        except ValueError:
            logging.error(
                "Invalid QDRANT_PORT %r, falling back to 6333",
                port_str,
            )
            self.port = 6333
        self.url = f"http://{self.host}:{self.port}"

        env_name = normalize_input(os.getenv("NODE_ENV", ""))
        # New env var name with backward compatibility for older deployments
        use_mock_env = os.getenv("USE_QDRANT_MOCK")
        if use_mock_env is None:  # pragma: no cover - deprecated env
            use_mock_env = os.getenv("QDRANT_USE_MOCK")
        use_mock = use_mock_env == "1" if use_mock_env is not None else False
        is_patched = QdrantClient is not None and _is_unittest_mock(
            QdrantClient
        )

        # Use mock in test/ci unless a test patched QdrantClient on purpose.
        if (env_name in {"test", "ci"} and not is_patched) or use_mock:
            self.client: Any = QdrantMock()
            return

        if QdrantClient is None:
            self.client = QdrantMock()
            return

        try:
            self.client = QdrantClient(host=self.host, port=self.port)
        except Exception as e:
            _lg().error("Failed to initialize Qdrant client: %s", e)
            self.client = None

    # Health ------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        if not self.client:
            _lg().error("Qdrant client not initialized")
            return {
                "status": "error",
                "message": "Qdrant client not initialized",
            }
        try:
            cols = self.client.get_collections()
            items = getattr(cols, "collections", []) or []
            return {
                "status": "healthy",
                "collections_count": len(items),
                "url": self.url,
            }
        except Exception as e:
            _lg().error("Qdrant health check failed: %s", e)
            return {"status": "error", "message": str(e)}

    # Collections --------------------------------------------------------

    def create_collection(self, collection_name: str, **kwargs: Any) -> bool:
        """Create or recreate a collection.

        Parameters
        ----------
        collection_name:
            Name of the collection to create.
        **kwargs:
            Extra parameters forwarded to the underlying client, such as
            ``vector_size`` and ``distance``.

        Returns
        -------
        bool
            ``True`` on success, ``False`` otherwise.
        """
        if not self.client:
            _lg().error("Qdrant client not initialized")
            return False
        try:
            return bool(
                self.client.create_collection(
                    collection_name=collection_name, **kwargs
                )
            )
        except Exception as e:
            _lg().error(
                "Failed to create collection %s: %s", collection_name, e
            )
            return False

    def collection_exists(self, name: str) -> bool:
        if not self.client:
            _lg().error("Qdrant client not initialized")
            return False
        try:
            cols = self.client.get_collections()
            items = getattr(cols, "collections", []) or []
            names = [getattr(c, "name", "") for c in items]
            return name in names
        except Exception as e:
            _lg().error("Failed to check collection existence: %s", e)
            return False

    def delete_collection(self, name: str) -> bool:
        if not self.client:
            _lg().error("Qdrant client not initialized")
            return False
        try:
            return bool(self.client.delete_collection(name))
        except Exception as e:
            _lg().error("Failed to delete collection %s: %s", name, e)
            return False

    def get_collection_info(self, name: str) -> Optional[Dict[str, Any]]:
        if not self.client:
            _lg().error("Qdrant client not initialized")
            return None
        try:
            info = self.client.get_collection(name)
            return {
                "name": name,
                "vectors_count": getattr(info, "vectors_count", 0),
                "indexed_vectors_count": getattr(
                    info, "indexed_vectors_count", 0
                ),
                "points_count": getattr(info, "points_count", 0),
                "status": getattr(info, "status", "unknown"),
            }
        except Exception as e:
            _lg().error("Failed to get collection info for %s: %s", name, e)
            return None

    # Points / Search ----------------------------------------------------

    def upsert_points(
        self,
        collection_name: str,
        points: List[Dict[str, Any]],
    ) -> bool:
        if not self.client:
            _lg().error("Qdrant client not initialized")
            return False
        try:
            return bool(
                self.client.upsert(
                    collection_name=collection_name, points=points
                )
            )
        except Exception as e:
            _lg().error(
                "Failed to upsert points to %s: %s", collection_name, e
            )
            return False

    def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
    ) -> List[Any]:
        if not self.client:
            _lg().error("Qdrant client not initialized")
            return []
        try:
            res = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True,
            )
            out: List[Any] = []
            for r in res:
                if hasattr(r, "__dict__"):
                    out.append(dict(r.__dict__))
                else:
                    out.append(r)
            return out
        except Exception as e:
            _lg().error(
                "Failed to search vectors in %s: %s", collection_name, e
            )
            return []


# ---------------------------------------------------------------------------
# Singleton API
# ---------------------------------------------------------------------------

_qdrant_singleton: Optional[QdrantService] = None


def get_qdrant_service() -> QdrantService:
    global _qdrant_singleton
    if _qdrant_singleton is None:
        _qdrant_singleton = QdrantService()
    return _qdrant_singleton


__all__ = ["QdrantService", "QdrantMock", "get_qdrant_service", "_retry"]
