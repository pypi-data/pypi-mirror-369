from dataclasses import dataclass, field
import os
import re
from typing import List

from server.config import settings


def _compile_forbidden_patterns(paths: List[str]) -> List[re.Pattern[str]]:
    """Compile regex patterns for sensitive paths that should be blocked."""
    patterns: List[re.Pattern[str]] = []
    for raw in paths:
        raw = raw.strip()
        if not raw:
            continue
        normalized = os.path.normpath(raw)
        escaped = re.escape(normalized)  # Treat path chars literally in regex
        if normalized.startswith("/"):
            patterns.append(
                re.compile(
                    rf"^{escaped}($|/)",
                    re.IGNORECASE,
                )
            )  # Absolute paths must match from filesystem root
        else:
            patterns.append(
                re.compile(
                    rf"(^|/){escaped}($|/)",
                    re.IGNORECASE,
                )
            )  # Relative paths can appear anywhere in the hierarchy
    return patterns


@dataclass
class AppConfig:
    """Application configuration settings."""

    qdrant_url: str | None = settings.QDRANT_URL
    qdrant_api_key: str | None = settings.QDRANT_API_KEY
    openai_api_key: str | None = settings.OPENAI_API_KEY
    qdrant_collection_name: str = "user_memories"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    chat_completion_model: str = "gpt-4o"
    not_found_threshold: int = 5
    sensitive_paths: List[str] = field(
        default_factory=lambda: settings.SENSITIVE_PATHS.copy()
    )
    allowed_origins_env: str | None = os.getenv("ALLOWED_ORIGINS")
    allowed_origins: List[str] = field(init=False)
    forbidden_path_patterns: List[re.Pattern[str]] = field(init=False)

    def __post_init__(self) -> None:
        base_origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://buildmode.ai",
        ]
        if self.allowed_origins_env:
            env_origins = [
                origin.strip()
                for origin in self.allowed_origins_env.split(",")
                if origin.strip()
            ]
            base_origins.extend(env_origins)
        self.allowed_origins = base_origins
        self.forbidden_path_patterns = _compile_forbidden_patterns(
            self.sensitive_paths
        )
