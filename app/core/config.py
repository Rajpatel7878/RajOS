from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "RajOS"
    APP_VERSION: str = "1.0.0"

    DEBUG: bool = True

    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()