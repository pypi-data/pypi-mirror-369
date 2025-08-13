"""Helper utilities for validating tasks during automated testing."""

from __future__ import annotations

import asyncio
import json
import os
import logging

# Directory used to store validation results
MEMORY_DIR = None


async def run_command(cmd: str) -> tuple[str, int]:
    """Execute a shell command asynchronously.

    Args:
        cmd: Command string to run in the system shell.

    Returns:
        A tuple containing the decoded combined stdout/stderr output and the
        process's exit code.
    """
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out, _ = await proc.communicate()
    return out.decode(), proc.returncode


def update_memory(category: str, key: str, data: dict) -> None:
    """Persist task validation data to disk.

    Args:
        category: Namespace grouping for the saved data.
        key: Identifier used in the file name.
        data: JSON-serializable dictionary to store.

    Returns:
        None
    """
    global MEMORY_DIR
    if MEMORY_DIR is None:
        MEMORY_DIR = os.path.join(os.getcwd(), "task_plans")
    os.makedirs(MEMORY_DIR, exist_ok=True)
    path = os.path.join(MEMORY_DIR, f"{category}_{key}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except OSError as exc:
        logging.warning("Failed to write validation data to %s: %s", path, exc)
