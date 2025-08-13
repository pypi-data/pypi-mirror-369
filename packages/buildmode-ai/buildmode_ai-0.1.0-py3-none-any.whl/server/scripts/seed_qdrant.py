#!/usr/bin/env python3
"""
Initial data seeding script for Qdrant.
Creates collections and adds sample vectors for testing.
"""

import sys
import os
import logging
import hashlib
import struct
from typing import List, Dict, Any

from qdrant_client.http.models import PointStruct, Distance
from server.services.qdrant_service import get_qdrant_service

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_placeholder_embedding(
    text: str, dimension: int = 384
) -> List[float]:
    """Generate a deterministic embedding for offline scripts."""
    hash_obj = hashlib.md5(text.encode())
    hash_bytes = hash_obj.digest()

    embedding = []
    for i in range(dimension):
        byte_idx = i % len(hash_bytes)
        value = struct.unpack("B", hash_bytes[byte_idx:byte_idx + 1])[0]
        normalized_value = (value / 255.0) * 2.0 - 1.0
        embedding.append(normalized_value)

    return embedding


def search_memory_vectors(
    query: str, collection_name: str = "memory_files", limit: int = 10
) -> List[Dict[str, Any]]:
    """Search memory using vector similarity in Qdrant."""
    service = get_qdrant_service()
    if not service.collection_exists(collection_name):
        return []

    query_vector = generate_placeholder_embedding(query)
    return service.search_vectors(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit,
        score_threshold=0.3,
    )


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_collections():
    """Create initial Qdrant collections."""
    collections = [
        {
            "name": "memory_files",
            "description": "Code file embeddings and metadata",
        },
        {
            "name": "memory_entries",
            "description": "General text embeddings and notes",
        },
    ]

    for collection in collections:
        name = collection["name"]
        service = get_qdrant_service()
        if service.collection_exists(name):
            logger.info(f"Collection {name} already exists")
        else:
            logger.info(f"Creating collection: {name}")
            if service.create_collection(
                collection_name=name,
                vector_size=384,
                distance=Distance.COSINE,
            ):
                logger.info(f"Successfully created collection: {name}")
            else:
                logger.error(f"Failed to create collection: {name}")
                return False

    return True


def seed_sample_data():
    """Add sample vectors for testing."""
    sample_files = [
        {
            "file_path": "server/main.py",
            "content": "FastAPI application main entry point with CORS "
            "middleware and health checks",
            "metadata": {
                "language": "Python",
                "file_size": 5000,
                "summary": "Main FastAPI application file",
                "functions": ["health_check"],
                "type": "sample",
            },
        },
        {
            "file_path": "server/models.py",
            "content": "SQLAlchemy database models for memory files, "
            "tasks, and user management",
            "metadata": {
                "language": "Python",
                "file_size": 8000,
                "summary": "Database models and schemas",
                "functions": ["MemoryFile", "TaskQueue", "User"],
                "type": "sample",
            },
        },
        {
            "file_path": "server/config.py",
            "content": "Application configuration settings using "
            "Pydantic for environment variables",
            "metadata": {
                "language": "Python",
                "file_size": 2000,
                "summary": "Configuration and settings management",
                "functions": ["Settings"],
                "type": "sample",
            },
        },
    ]

    sample_entries = [
        {
            "file_path": "docs/api_design.md",
            "content": "API design principles and REST endpoint "
            "conventions for the BuildMode.AI platform",
            "metadata": {
                "summary": "API design documentation",
                "notes": "Contains guidelines for endpoint naming and "
                "response formats",
                "type": "sample",
            },
        },
        {
            "file_path": "docs/deployment.md",
            "content": "Deployment guide for Railway platform including "
            "environment variables and service configuration",
            "metadata": {
                "summary": "Deployment documentation",
                "notes": "Step-by-step deployment instructions",
                "type": "sample",
            },
        },
    ]

    logger.info("Seeding sample data...")

    points = []
    for file_data in sample_files:
        embedding = generate_placeholder_embedding(file_data["content"])
        point = PointStruct(
            id=hash(file_data["file_path"]) % (2**63),
            vector=embedding,
            payload={
                "file_path": file_data["file_path"],
                "content": file_data["content"],
                **file_data["metadata"],
            },
        )
        points.append(point)

    if points:
        service = get_qdrant_service()
        if service.upsert_points("memory_files", points):
            logger.info(
                f"Added {len(points)} sample files to memory_files collection"
            )
        else:
            logger.error("Failed to add sample files")
            return False

    points = []
    for entry_data in sample_entries:
        embedding = generate_placeholder_embedding(entry_data["content"])
        point = PointStruct(
            id=hash(f"entry_{entry_data['file_path']}") % (2**63),
            vector=embedding,
            payload={
                "file_path": entry_data["file_path"],
                "content": entry_data["content"],
                **entry_data["metadata"],
            },
        )
        points.append(point)

    if points:
        service = get_qdrant_service()
        if service.upsert_points("memory_entries", points):
            logger.info(
                f"Added {len(points)} sample entries to memory_entries "
                f"collection"
            )
        else:
            logger.error("Failed to add sample entries")
            return False

    return True


def verify_setup():
    """Verify that collections and data were created successfully."""
    logger.info("Verifying Qdrant setup...")

    collections = ["memory_files", "memory_entries"]
    for collection_name in collections:
        service = get_qdrant_service()
        if service.collection_exists(collection_name):
            info = service.get_collection_info(collection_name)
            if info:
                logger.info(
                    f"✓ Collection {collection_name}: "
                    f"{info['points_count']} points, status: {info['status']}"
                )
            else:
                logger.warning(
                    f"⚠ Could not get info for collection {collection_name}"
                )
        else:
            logger.error(f"✗ Collection {collection_name} does not exist")
            return False

    test_query = "FastAPI application"
    try:
        results = search_memory_vectors(test_query, "memory_files", limit=3)
        logger.info(
            f"✓ Test search for '{test_query}' returned {len(results)} results"
        )
    except Exception as e:
        logger.error(f"✗ Test search failed: {e}")
        return False

    return True


def main():
    """Main seeding function."""
    logger.info("Starting Qdrant seeding process...")

    service = get_qdrant_service()
    health = service.health_check()
    if health.get("status") != "healthy":
        logger.error(f"Qdrant is not healthy: {health}")
        return False

    logger.info(f"Qdrant is healthy: {health}")

    if not create_collections():
        logger.error("Failed to create collections")
        return False

    if not seed_sample_data():
        logger.error("Failed to seed sample data")
        return False

    if not verify_setup():
        logger.error("Setup verification failed")
        return False

    logger.info("Qdrant seeding completed successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
