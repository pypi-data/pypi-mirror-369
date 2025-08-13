"""Kairos chat agent using OpenAI's chat completion API."""

from fastapi import HTTPException
import httpx

from server.config import settings


async def run(prompt: str) -> str:
    """Send a prompt to OpenAI and return the assistant's reply."""
    api_key = settings.OPENAI_API_KEY
    # Ensure an API key is configured before attempting any network calls
    if not api_key or not api_key.strip():
        raise HTTPException(
            status_code=500, detail={"code": "OPENAI_KEY_MISSING"}
        )

    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        detail = e.response.text or "OpenAI request failed"
        raise HTTPException(status_code=e.response.status_code, detail=detail)
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Error communicating with OpenAI. Please try again later.",
        )

    try:
        completion = response.json()
        return completion["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError):
        raise HTTPException(
            status_code=500, detail="Unexpected OpenAI response format"
        )
