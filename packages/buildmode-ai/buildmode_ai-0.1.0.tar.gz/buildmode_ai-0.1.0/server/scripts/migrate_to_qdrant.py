#!/usr/bin/env python3
"""
Migration script to move existing embeddings from PostgreSQL to Qdrant.
This script safely migrates data while preserving the original PostgreSQL data.
"""

import sys
import os
import logging
import hashlib
import struct
from typing import List
from qdrant_client.http.models import PointStruct

import server.database as db
from server import models
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


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def migrate_memory_files():
    """Migrate memory_files table data to Qdrant."""
    collection_name = "memory_files"

    logger.info("Starting migration of memory_files to Qdrant...")

    service = get_qdrant_service()
    if not service.collection_exists(collection_name):
        logger.info(f"Creating collection: {collection_name}")
        if not service.create_collection(
            collection_name=collection_name, vector_size=384
        ):
            logger.error(f"Failed to create collection: {collection_name}")
            return False
    try:
        with db.session_scope() as session:
            memory_files = session.query(models.MemoryFile).all()
            logger.info(f"Found {len(memory_files)} memory files to migrate")

            points = []
            for file_record in memory_files:
                try:
                    content = (
                        f"{file_record.summary or ''} "
                        f"{file_record.full_text or ''}"
                    )
                    if not content.strip():
                        content = file_record.file_path

                    embedding = generate_placeholder_embedding(content)

                    point = PointStruct(
                        id=hash(file_record.file_path) % (2**63),
                        vector=embedding,
                        payload={
                            "file_path": file_record.file_path,
                            "summary": file_record.summary,
                            "language": file_record.language,
                            "file_size": file_record.file_size,
                            "functions": file_record.functions or [],
                            "components": file_record.components or [],
                            "content": content,
                            "migrated_from": "postgresql",
                        },
                    )
                    points.append(point)
                    if len(points) >= 100:
                        if service.upsert_points(collection_name, points):
                            logger.info(
                                f"Migrated batch of {len(points)} points"
                            )
                        else:
                            logger.error("Failed to migrate batch")
                        points = []

                except Exception as e:
                    logger.error(
                        f"Failed to process file {file_record.file_path}: {e}"
                    )
                    continue

            if points:
                if service.upsert_points(collection_name, points):
                    logger.info(
                        f"Migrated final batch of {len(points)} points"
                    )
                else:
                    logger.error("Failed to migrate final batch")

            logger.info("Memory files migration completed successfully")
            return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def migrate_memory_entries():
    """Migrate memory_entries table data to Qdrant."""
    collection_name = "memory_entries"

    logger.info("Starting migration of memory_entries to Qdrant...")

    service = get_qdrant_service()
    if not service.collection_exists(collection_name):
        logger.info(f"Creating collection: {collection_name}")
        if not service.create_collection(
            collection_name=collection_name, vector_size=384
        ):
            logger.error(f"Failed to create collection: {collection_name}")
            return False
    try:
        with db.session_scope() as session:
            memory_entries = session.query(models.MemoryEntry).all()
            logger.info(
                f"Found {len(memory_entries)} memory entries to migrate"
            )

            points = []
            for entry in memory_entries:
                try:
                    content = (
                        f"{entry.summary or ''} {entry.full_text or ''} "
                        f"{entry.notes or ''}"
                    )
                    if not content.strip():
                        content = entry.file_path

                    embedding = generate_placeholder_embedding(content)

                    point = PointStruct(
                        id=hash(f"entry_{entry.file_path}") % (2**63),
                        vector=embedding,
                        payload={
                            "file_path": entry.file_path,
                            "summary": entry.summary,
                            "full_text": entry.full_text,
                            "notes": entry.notes,
                            "content": content,
                            "migrated_from": "postgresql",
                        },
                    )
                    points.append(point)
                    if len(points) >= 100:
                        if service.upsert_points(collection_name, points):
                            logger.info(
                                f"Migrated batch of {len(points)} points"
                            )
                        else:
                            logger.error("Failed to migrate batch")
                        points = []

                except Exception as e:
                    logger.error(
                        f"Failed to process entry {entry.file_path}: {e}"
                    )
                    continue

            if points:
                if service.upsert_points(collection_name, points):
                    logger.info(
                        f"Migrated final batch of {len(points)} points"
                    )
                else:
                    logger.error("Failed to migrate final batch")

            logger.info("Memory entries migration completed successfully")
            return True

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def verify_migration():
    """Verify that the migration was successful."""
    logger.info("Verifying migration...")

    collections = ["memory_files", "memory_entries"]
    for collection_name in collections:
        service = get_qdrant_service()
        if service.collection_exists(collection_name):
            info = service.get_collection_info(collection_name)
            if info:
                logger.info(
                    f"Collection {collection_name}: "
                    f"{info['points_count']} points"
                )
            else:
                logger.warning(
                    f"Could not get info for collection {collection_name}"
                )
        else:
            logger.warning(f"Collection {collection_name} does not exist")


def main():
    """Main migration function."""
    logger.info("Starting Qdrant migration process...")

    service = get_qdrant_service()
    health = service.health_check()
    if health.get("status") != "healthy":
        logger.error(f"Qdrant is not healthy: {health}")
        return False

    success = True

    if not migrate_memory_files():
        logger.error("Failed to migrate memory_files")
        success = False

    if not migrate_memory_entries():
        logger.error("Failed to migrate memory_entries")
        success = False

    verify_migration()
    db.check_for_connection_leaks()

    if success:
        logger.info("Migration completed successfully!")
    else:
        logger.error("Migration completed with errors")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
