"""Helpers for working with Qdrant."""

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from server.config import settings


COLLECTION = "kairos_memories"
_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    """Return a singleton Qdrant client instance."""

    global _client
    if _client is None:
        _client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.QDRANT_API_KEY,
            prefer_grpc=False,
        )
    return _client


def ensure_collection(vector_size: int = 1536) -> None:
    """Ensure the default collection exists."""

    client = get_client()
    try:
        client.get_collection(COLLECTION)
    except Exception:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )
