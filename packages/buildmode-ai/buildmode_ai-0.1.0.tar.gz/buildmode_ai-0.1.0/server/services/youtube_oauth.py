"""Deprecated YouTube OAuth endpoints.

This module previously provided endpoints for performing a YouTube OAuth
flow. The functionality has been removed from the open source project and the
routes are kept only to return a 404 response.
"""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/auth/youtube", tags=["youtube-oauth"])


@router.get("/login")
async def login(_: Request):  # pragma: no cover - simple passthrough
    """Disabled login endpoint."""
    raise HTTPException(status_code=404, detail="YouTube OAuth disabled")


@router.get("/callback")
async def oauth_callback(_: Request):  # pragma: no cover - simple passthrough
    """Disabled callback endpoint."""
    raise HTTPException(status_code=404, detail="YouTube OAuth disabled")


__all__ = ["router"]
