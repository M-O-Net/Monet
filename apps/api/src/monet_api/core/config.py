from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Managed Postgres (Render, Neon, Supabase) hands out a libpq URL: no driver, and libpq-only
# query args that asyncpg.connect() rejects by name.
_LIBPQ_SCHEMES = ("postgres", "postgresql")
_ASYNCPG_RENAMED = {"sslmode": "ssl"}
_ASYNCPG_UNSUPPORTED = ("channel_binding",)


def as_asyncpg_url(url: str) -> str:
    """Return the URL with the asyncpg driver and query args asyncpg accepts."""
    parts = urlsplit(url)
    if parts.scheme not in _LIBPQ_SCHEMES:
        return url
    query = [
        (_ASYNCPG_RENAMED.get(key, key), value)
        for key, value in parse_qsl(parts.query)
        if key not in _ASYNCPG_UNSUPPORTED
    ]
    return urlunsplit(
        ("postgresql+asyncpg", parts.netloc, parts.path, urlencode(query), parts.fragment)
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # No default — same reasoning as docker-compose.yml's required POSTGRES_PASSWORD: a
    # weak default here is one a real deploy could silently inherit. Set it in .env.
    database_url: str
    cors_origins: list[str] = ["http://localhost:5173"]

    _use_asyncpg = field_validator("database_url")(as_asyncpg_url)


settings = Settings()
