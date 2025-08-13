"""Terminal command execution route.

This module exposes an endpoint for executing a limited set of shell
commands. The endpoint is protected by authentication and only allows a
whitelisted list of safe commands. It uses ``create_subprocess_exec`` with
``shlex`` parsing to avoid shell injection vulnerabilities.
"""

import asyncio
import logging
import shlex

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from server.auth import auth_guard

router = APIRouter(prefix="/terminal", tags=["terminal"])

# Whitelist of allowed commands. These commands are considered safe and are
# executed directly without a shell.
ALLOWED_COMMANDS = {"ls", "pwd", "echo"}


class CommandRequest(BaseModel):
    command: str


@router.post("/execute")
async def execute_command(
    request: CommandRequest, user: dict = Depends(auth_guard)
) -> dict:
    """Execute a whitelisted shell command and return its output.

    The command string is tokenized with :func:`shlex.split` to prevent shell
    injection. Only commands present in ``ALLOWED_COMMANDS`` are permitted.
    """

    if not request.command or not request.command.strip():
        raise HTTPException(status_code=400, detail="Command is required")

    try:
        parts = shlex.split(request.command)
    except ValueError as exc:  # malformed command
        raise HTTPException(status_code=400, detail="Invalid command") from exc

    if not parts:
        raise HTTPException(status_code=400, detail="Command is required")

    cmd, *args = parts
    if cmd not in ALLOWED_COMMANDS:
        logging.warning("Command not allowed: %s", request.command)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Command not allowed",
        )

    logging.info("Executing command: %s", request.command)

    try:
        process = await asyncio.create_subprocess_exec(
            cmd,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except Exception:
        logging.exception("Failed to execute command: %s", request.command)
        raise HTTPException(status_code=500, detail="Internal server error")

    stdout, _ = await process.communicate()
    output = stdout.decode().strip()
    if process.returncode != 0:
        raise HTTPException(status_code=400, detail=output)
    return {"output": output}
