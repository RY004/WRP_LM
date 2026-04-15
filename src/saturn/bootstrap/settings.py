"""Runtime settings for the Saturn service."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Saturn"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://saturn:saturn@localhost:5432/saturn"
    database_echo: bool = False
    database_pool_size: int = Field(default=5, ge=1)
    database_max_overflow: int = Field(default=10, ge=0)
    redis_url: str = "redis://localhost:6379/0"
    storage_backend: Literal["filesystem", "s3"] = "filesystem"
    storage_filesystem_root: Path = Path("./data/blobs")
    storage_s3_endpoint: str | None = None
    storage_s3_bucket: str | None = None
    storage_s3_access_key: str | None = None
    storage_s3_secret_key: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_uri: str | None = None
    notion_client_id: str | None = None
    notion_client_secret: str | None = None
    notion_redirect_uri: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator(
        "storage_s3_endpoint",
        "storage_s3_bucket",
        "storage_s3_access_key",
        "storage_s3_secret_key",
        "google_client_id",
        "google_client_secret",
        "google_redirect_uri",
        "notion_client_id",
        "notion_client_secret",
        "notion_redirect_uri",
        mode="before",
    )
    @classmethod
    def empty_string_as_none(cls, value: object) -> object:
        if value == "":
            return None
        return value

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def validate_storage_configuration(self) -> "Settings":
        if self.storage_backend == "s3" and not self.storage_s3_bucket:
            raise ValueError("STORAGE_S3_BUCKET is required when STORAGE_BACKEND=s3")
        return self

    @property
    def is_development(self) -> bool:
        return self.app_env in {"development", "local", "test"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
