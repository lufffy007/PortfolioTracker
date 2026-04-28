"""
Application configuration using environment variables.

In .NET terms, this is similar to:
- `appsettings.json` values
- bound into a strongly-typed options class
- injected where needed

We use Pydantic Settings to read values from:
- `.env` (for local development)
- or real environment variables (for deployment)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Strongly-typed settings for this project.

    Important beginner note:
    - We provide empty-string defaults so the server can boot even if `.env`
      is not created yet.
    - Actual SnapTrade endpoints will still fail with a clear message until
      you set real keys.
    """

    SNAPTRADE_CLIENT_ID: str = ""
    SNAPTRADE_CONSUMER_KEY: str = ""
    ENVIRONMENT: str = "development"
    APP_NAME: str = "Portfolio Tracker Backend"
    APP_ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./portfolio.db"
    CORS_ALLOW_ORIGINS: str = "http://localhost:8501,http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached settings object.

    Comparable to a singleton options object in .NET DI.
    """

    return Settings()


# Compatibility alias for any modules that still import `settings` directly.
settings = get_settings()

