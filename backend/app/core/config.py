from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "IoTSense API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = Field(
        default="postgresql+psycopg://iotsense:iotsense@localhost:5432/iotsense"
    )
    log_level: str = "INFO"
    session_cookie_name: str = "iotsense_session"
    csrf_cookie_name: str = "iotsense_csrf"
    secure_cookies: bool = True
    session_ttl_hours: int = 12
    password_reset_ttl_minutes: int = 30
    login_rate_limit_attempts: int = 5
    login_rate_limit_window_seconds: int = 900
    cors_origins: list[str] = Field(default_factory=list)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_starttls: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
