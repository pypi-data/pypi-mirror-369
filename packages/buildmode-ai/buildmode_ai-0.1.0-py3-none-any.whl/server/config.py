"""Application configuration and environment helpers."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices
from typing import Optional
import logging
import os
import re


# Select environment file based on NODE_ENV before loading settings
NODE_ENV = os.getenv("NODE_ENV", "development")
ENV_FILE = f".env.{NODE_ENV}"
load_dotenv(ENV_FILE)
os.environ.setdefault("ENV", NODE_ENV)


def _ensure_psycopg_driver(url: str) -> str:
    """Rewrite PostgreSQL URLs lacking a driver spec to use psycopg."""
    lower = url.lower()
    if lower.startswith("postgresql+"):
        return url
    if lower.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://"):]
    if lower.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://"):]
    return url


def _normalize_env_keys() -> None:
    """Normalize environment variable names by stripping whitespace.

    Some deployment environments may accidentally introduce leading or
    trailing spaces in variable names. This helper ensures that the trimmed
    version of each key is available in ``os.environ`` so Pydantic can resolve
    it using the standard alias without needing space-prefixed variants.
    """
    for key, value in list(os.environ.items()):
        stripped = key.strip()
        if stripped != key and stripped not in os.environ:
            os.environ[stripped] = value


_normalize_env_keys()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "RAILWAY_DATABASE_URL"),
    )
    GH_PAT: Optional[str] = Field(default=None)
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    QDRANT_URL: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("QDRANT_URL", " QDRANT_URL"),
    )
    SUPABASE_REGION: Optional[str] = Field(default="us-east-1")
    SUPABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None)

    DB_USER: Optional[str] = Field(default=None)
    DB_PASSWORD: Optional[str] = Field(default=None)
    DB_HOST: Optional[str] = Field(default=None)
    DB_PORT: Optional[int] = Field(default=None)
    DB_NAME: Optional[str] = Field(default=None)

    SESSION_SECRET_KEY: Optional[str] = Field(default=None)
    LLM_RATE_LIMIT_PER_MIN: int = Field(default=60)
    ENV: str = Field(default="development")
    QDRANT_API_KEY: Optional[str] = Field(default=None)
    SENSITIVE_PATHS: list[str] = Field(
        default_factory=lambda: [
            ".env",
            ".git",
            ".ssh",
            "/etc",
            "aws_keys.json",
        ],
        validation_alias=AliasChoices("SENSITIVE_PATHS"),
        json_schema_extra={"env": "SENSITIVE_PATHS"},
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_prefix="",
        extra="ignore",  # allow Vite-only vars
        env_parse_delimiter=",",
    )

    @property
    def database_url(self) -> str:
        """Return the configured database URL with driver normalization.

        - Prefers `DATABASE_URL`/`RAILWAY_DATABASE_URL` when set.
        - In production with Supabase direct URLs, switches to pooler if
          possible.
        - Ensures sslmode=require for Supabase if missing.
        - Falls back to SQLite when no DB env is provided.
        """
        if self.DATABASE_URL:
            url = str(self.DATABASE_URL)
            if self.ENV.lower() == "production" and "supabase.co" in url:
                pooler_url = self.supabase_pooler_url
                if pooler_url:
                    url = pooler_url
            if "supabase.co" in url and "sslmode=" not in url:
                separator = "&" if "?" in url else "?"
                url += f"{separator}sslmode=require"
            return _ensure_psycopg_driver(url)

        missing = [
            var
            for var in (
                "DB_USER",
                "DB_PASSWORD",
                "DB_HOST",
                "DB_PORT",
                "DB_NAME",
            )
            if not getattr(self, var)
        ]
        if not missing:
            from urllib.parse import quote_plus

            encoded_password = quote_plus(str(self.DB_PASSWORD))
            url = (
                f"postgresql://{self.DB_USER}:{encoded_password}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
            return _ensure_psycopg_driver(url)

        logging.warning(
            "Missing database configuration: %s. Using SQLite fallback.",
            missing,
        )
        return "sqlite:///./buildmode.db"

    @property
    def qdrant_url(self) -> str:
        """Return the configured Qdrant service URL."""
        if self.QDRANT_URL:
            return str(self.QDRANT_URL)
        return "http://buildmode-qdrant:6333"

    @property
    def supabase_pooler_url(self) -> str:
        """Convert a direct Supabase connection string to a pooler URL.

        Returns:
            The pooler URL if conversion succeeds; otherwise an empty string.
        """
        if self.DATABASE_URL and "supabase.co" in str(self.DATABASE_URL):
            url_str = str(self.DATABASE_URL)
            try:
                # Extract password and project ID from canonical Supabase URL
                match = re.match(
                    r"postgresql(?:\+[^:]*)?://postgres:([^@]+)@db\.([^.]+)\."
                    r"supabase\.co:5432/postgres",
                    url_str,
                )
                if match:
                    password, project_id = match.groups()
                    region = self.SUPABASE_REGION or "us-east-1"

                    from urllib.parse import quote_plus

                    encoded_password = quote_plus(password)

                    pooler_url = (
                        f"postgresql://postgres.{project_id}:"
                        f"{encoded_password}@aws-0-{region}."
                        f"pooler.supabase.com:5432/postgres"
                    )
                    pooler_url = _ensure_psycopg_driver(pooler_url)
                    logging.info(
                        "Converting direct Supabase connection to pooler: %s",
                        pooler_url.replace(encoded_password, "***"),
                    )
                    return pooler_url

                # Could not parse canonical format
                try:
                    masked = url_str.replace(
                        url_str.split(":")[2].split("@")[0],
                        "***",
                    )
                except Exception:
                    masked = "***"
                logging.warning(
                    "Failed to parse Supabase URL format: %s",
                    masked,
                )
            except Exception as e:
                logging.error(
                    "Error converting Supabase URL to pooler format: %s",
                    e,
                )

        return (
            _ensure_psycopg_driver(str(self.DATABASE_URL))
            if self.DATABASE_URL
            else ""
        )


STRICT_ENV = os.getenv("STRICT_ENV") == "1"

settings = Settings()

if not settings.OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY is not set. Running without LLM access.")

# Fail fast in production if required environment variables are missing
if settings.ENV.lower() == "production":
    logging.info(
        "Running in production mode - validating required environment "
        "variables"
    )

    logging.info(f"Environment variable count: {len(os.environ)}")

    qdrant_env = os.getenv("QDRANT_URL")
    logging.info(f"QDRANT_URL from environment: {repr(qdrant_env)}")
    logging.info(
        f"QDRANT_URL resolved from settings: {repr(settings.qdrant_url)}"
    )
    logging.info(f"QDRANT_API_KEY set: {bool(os.getenv('QDRANT_API_KEY'))}")

    railway_vars = [
        key for key in os.environ.keys() if "RAILWAY" in key.upper()
    ]
    if railway_vars:
        logging.info("Railway environment variables found: %s", railway_vars)

    qdrant_vars = [key for key in os.environ.keys() if "QDRANT" in key.upper()]
    if qdrant_vars:
        logging.info(
            "Qdrant-related environment variables found: %s",
            qdrant_vars,
        )
    else:
        logging.warning(
            "No Qdrant-related environment variables found in os.environ"
        )

    missing_vars: list[str] = []
    optional_vars: list[str] = []

    if not (os.getenv("DATABASE_URL") or os.getenv("RAILWAY_DATABASE_URL")):
        optional_vars.append("DATABASE_URL")

    # These environment variables are useful for full functionality but
    # should not cause the application to fail, even in strict mode.
    for optional in ["GH_PAT", "OPENAI_API_KEY", "QDRANT_API_KEY"]:
        if not os.getenv(optional):
            optional_vars.append(optional)

    session_secret = os.getenv("SESSION_SECRET_KEY")
    if not session_secret:
        missing_vars.append("SESSION_SECRET_KEY")

    if not os.getenv("QDRANT_URL"):
        logging.warning(
            "QDRANT_URL is not set; falling back to %s",
            settings.qdrant_url,
        )

    if optional_vars:
        logging.warning(
            "Missing optional environment variables: %s",
            ", ".join(optional_vars),
        )

    if missing_vars:
        error_msg = (
            "Missing required environment variables in production: "
            f"{', '.join(missing_vars)}"
        )
        if STRICT_ENV:
            logging.critical(error_msg)
            raise RuntimeError(error_msg)
        logging.warning(error_msg + " (continuing due to non-strict mode)")
