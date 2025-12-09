from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from environment (12-factor)."""

    # Database - NO DEFAULT CREDENTIALS (security)
    database_url: str = Field(
        description="Database connection URL",
        alias="DATABASE_URL",
    )
    echo_sql: bool = Field(default=False, alias="ECHO_SQL")
    
    # Security
    secret_key: str = Field(
        description="Secret key for JWT/sessions",
        alias="SECRET_KEY",
    )
    allowed_hosts: list[str] = Field(
        default=["localhost"],
        alias="ALLOWED_HOSTS"
    )
    
    # API Configuration
    api_title: str = Field(default="User Service", alias="API_TITLE")
    api_version: str = Field(default="1.0.0", alias="API_VERSION")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
    )


settings = Settings()
