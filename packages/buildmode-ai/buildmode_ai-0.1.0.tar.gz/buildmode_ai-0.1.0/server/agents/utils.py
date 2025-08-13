"""Utilities for agent text normalization and rate limiting."""

import asyncio
from typing import Optional

from server.config import settings


#: Interval in seconds for the rate limiter to replenish a token.
RATE_LIMIT_PERIOD_SECONDS = 60.0
"""Length of one rate-limiting window in seconds."""


def normalize_input(text: str) -> str:
    """Normalize arbitrary user-provided text.

    Args:
        text: String potentially containing mixed case and surrounding
            whitespace.

    Returns:
        A lowercase string with surrounding whitespace removed.
    """
    return text.strip().lower()


class LLMRateLimiter:
    """Simple token bucket style limiter for LLM requests."""

    def __init__(self, rate_per_min: int):
        """Initialize the limiter.

        Args:
            rate_per_min: Allowed requests per minute.
        """
        self.semaphore = asyncio.BoundedSemaphore(rate_per_min)
        self.period = RATE_LIMIT_PERIOD_SECONDS

    async def acquire(self) -> None:
        """Acquire a token, blocking until one becomes available."""
        await self.semaphore.acquire()
        asyncio.create_task(self._release_after_delay())

    async def _release_after_delay(self) -> None:
        """Release a token after the rate-limit period elapses."""
        await asyncio.sleep(self.period)
        self.semaphore.release()


_limiter: Optional[LLMRateLimiter] = None


def get_llm_limiter() -> LLMRateLimiter:
    """Retrieve the shared LLM rate limiter.

    Returns:
        The singleton :class:`LLMRateLimiter` used across the application.
    """
    global _limiter
    if _limiter is None:
        _limiter = LLMRateLimiter(settings.LLM_RATE_LIMIT_PER_MIN)
    return _limiter
