"""Database connection and session management for RajOS FastAPI backend.

Configured via pydantic-settings to dynamically load DATABASE_URL from
environment variables or a .env file without hardcoded paths or credentials.
Supports SQLite, PostgreSQL, and other SQLAlchemy-compatible databases.
"""

from typing import Generator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session


class DatabaseSettings(BaseSettings):
    """Database configuration loaded from environment variables or .env."""

    DATABASE_URL: str = "sqlite:///./rajos.db"

    # Connection pool options (for PostgreSQL / MySQL / external DBs)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instantiate settings from environment / .env
db_settings = DatabaseSettings()

# Normalize legacy postgres:// scheme to postgresql:// (e.g. Heroku, Supabase, Neon)
raw_url = db_settings.DATABASE_URL
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)

# SQLite requires check_same_thread=False for multi-threaded FastAPI execution.
# PostgreSQL/MySQL reject this argument and require pool configuration instead.
connect_args = {}
engine_kwargs = {}

if raw_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    engine_kwargs["pool_size"] = db_settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = db_settings.DB_MAX_OVERFLOW
    engine_kwargs["pool_pre_ping"] = db_settings.DB_POOL_PRE_PING

engine = create_engine(
    raw_url,
    connect_args=connect_args,
    **engine_kwargs,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a SQLAlchemy database session and ensuring its closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
