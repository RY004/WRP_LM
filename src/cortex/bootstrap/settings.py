"""Runtime settings scaffold."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg://saturn:saturn@localhost:5432/saturn"
    redis_url: str = "redis://localhost:6379/0"
    storage_backend: str = "filesystem"
    storage_filesystem_root: str = "./data/blobs"
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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
