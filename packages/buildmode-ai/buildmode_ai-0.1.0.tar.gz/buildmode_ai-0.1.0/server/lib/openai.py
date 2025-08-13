"""Lightweight wrappers around OpenAI's HTTP API."""

from typing import List

import httpx

from server.config import settings


OPENAI_BASE_URL = "https://api.openai.com/v1"


async def embed_text(text: str) -> List[float]:
    """Return the embedding vector for ``text`` using
    ``text-embedding-ada-002``."""

    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    payload = {"input": text, "model": "text-embedding-ada-002"}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{OPENAI_BASE_URL}/embeddings",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]


async def chat(prompt: str) -> str:
    """Generate a chat response using the ``gpt-4o-mini`` model."""

    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
