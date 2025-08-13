"""Route for remotely triggering the project's test suite.

This endpoint is primarily intended for internal or development use. To
prevent unauthorized execution of the test suite (which could be abused to
consume resources), the route now requires authentication via the standard
``auth_guard`` dependency used elsewhere in the application.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException

from server.auth import auth_guard

router = APIRouter(prefix="/test-agent", tags=["test-runner"])


@router.post("/run")
async def run_tests(user: dict = Depends(auth_guard)):
    """Run the test suite and return the results."""
    try:
        process = await asyncio.create_subprocess_exec(
            "pytest",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return {
            "returncode": process.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
