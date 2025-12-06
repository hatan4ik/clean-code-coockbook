from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from environment (12-factor)."""

    database_url: str = Field(
        default="postgresql+asyncpg://user:pass@localhost:5432/db",
        alias="DATABASE_URL",
    )
    echo_sql: bool = Field(default=False, alias="ECHO_SQL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
    )


settings = Settings()
