from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

from server.config import settings

router = APIRouter(prefix="/openai", tags=["openai"])


class ModelPrompt(BaseModel):
    model: str
    prompt: str


async def _proxy_openai(data: ModelPrompt):
    """Proxy requests to OpenAI's chat completion API using server-side key."""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=500, detail="OpenAI API key not configured"
        )

    payload = {
        "model": data.model,
        "messages": [{"role": "user", "content": data.prompt}],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        # Surface the error body from OpenAI if available
        detail = e.response.text or "OpenAI request failed"
        raise HTTPException(status_code=e.response.status_code, detail=detail)
    except httpx.RequestError:
        # Any network/connection error
        raise HTTPException(
            status_code=502,
            detail="Error communicating with OpenAI. Please try again later.",
        )

    try:
        completion = response.json()
        content = completion["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError):
        raise HTTPException(
            status_code=500, detail="Unexpected OpenAI response format"
        )

    return {"response": content}


@router.post("/call")
async def call_openai(data: ModelPrompt):
    return await _proxy_openai(data)


@router.post("/kairos")
async def call_openai_kairos(data: ModelPrompt):
    return await _proxy_openai(data)
