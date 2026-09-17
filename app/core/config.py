"""RajOS Application Settings.

All sensitive values are loaded from environment variables or a .env file.
No secrets are hardcoded here.

Required .env variables:
    SECRET_KEY                  - Long, random string for JWT signing (REQUIRED in production)
    DATABASE_URL                - SQLAlchemy DB URL (default: sqlite:///./rajos.db)
    DEFAULT_LLM_PROVIDER        - 'gemini', 'openai', or 'local' (default: 'gemini')
    GEMINI_API_KEY              - Your Google AI Studio API key
    OPENAI_API_KEY              - Your OpenAI API key (optional)
    CORS_ORIGINS                - Comma-separated list of allowed frontend origins
    ACCESS_TOKEN_EXPIRE_MINUTES - JWT token lifetime in minutes (default: 10080 = 7 days)
    DEBUG                       - true/false (default: false in production)
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "RajOS"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    API_V1_STR: str = "/api/v1"

    # ---------------------------------------------------------------
    # SECURITY — must be overridden in production via environment var.
    # The default here is intentionally non-secret and will only be
    # used in local development if .env is missing.
    # ---------------------------------------------------------------
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_USE_A_LONG_RANDOM_SECRET_KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # ---------------------------------------------------------------
    # DATABASE
    # ---------------------------------------------------------------
    DATABASE_URL: str = "sqlite:///./rajos.db"

    # ---------------------------------------------------------------
    # CORS — comma-separated allowed origins (override in production)
    # Example: "https://rajos.app,https://www.rajos.app"
    # ---------------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # ---------------------------------------------------------------
    # LLM PROVIDERS
    # ---------------------------------------------------------------
    DEFAULT_LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def get_cors_origins(self) -> List[str]:
        """Parse the CORS_ORIGINS comma-separated string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
