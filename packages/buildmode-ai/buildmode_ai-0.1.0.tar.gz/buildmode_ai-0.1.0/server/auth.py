import logging

import httpx
from fastapi import Header, HTTPException, status
from server.config import settings


logger = logging.getLogger(__name__)


async def auth_guard(authorization: str = Header(None)) -> dict:
    """Validate Supabase JWTs using the Supabase auth endpoint.

    The ``Authorization`` header must contain a ``Bearer`` token issued by
    Supabase. The token is verified by calling the ``/auth/v1/user`` endpoint
    with the project's anon key. On success the decoded user object is
    returned, otherwise ``401`` is raised.
    """

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing Authorization header.",
        )

    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase configuration is missing",
        )

    token = authorization.split(" ", 1)[1]
    url = f"{settings.SUPABASE_URL}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": settings.SUPABASE_ANON_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
    except httpx.RequestError:
        logger.exception("Supabase auth service request failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Service Unavailable: unable to reach Supabase auth service."
            ),
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    return resp.json()
