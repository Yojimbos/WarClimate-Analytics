from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "WarClimate_Analytics"
    app_env: str = Field(default="local", alias="APP_ENV")
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(
        default="postgresql+psycopg://demo:demo@localhost:5432/war_climate_analytics",
        alias="DATABASE_URL",
    )
    admin_api_key: str = Field(default="dev-admin-key", alias="ADMIN_API_KEY")
    cors_origins: str = Field(default="http://localhost:8080", alias="CORS_ORIGINS")
    losses_provider: str = Field(default="sample", alias="LOSSES_PROVIDER")
    weather_provider: str = Field(default="sample", alias="WEATHER_PROVIDER")
    request_timeout_seconds: float = 15.0
    data_dir: Path = Path("sample_data")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
