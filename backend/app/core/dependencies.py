from collections.abc import Generator

from app.core.config import Settings, get_settings_cached
from app.db.session import SessionLocal


def get_settings() -> Settings:
    """
    Dependency that returns application settings.
    """
    return get_settings_cached()


def get_db() -> Generator:
    """
    Dependency that yields a database session and ensures proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

