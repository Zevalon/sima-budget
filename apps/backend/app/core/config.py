from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "SIMA"
    app_debug: bool = False
    database_url: str = "postgresql+psycopg://sima:change-me-local-only@localhost:5432/sima"
    frontend_origin: str = "http://localhost:5173"
    trusted_hosts: str = "localhost,127.0.0.1,testserver"
    session_cookie_name: str = "sima_session"
    session_secret: str = "development-only-change-me"
    session_ttl_seconds: int = 28_800
    csrf_secret: str = "development-only-change-me"
    file_storage_driver: Literal["local", "s3"] = "local"
    file_storage_path: str = "../../runtime/uploads"
    max_upload_size_mb: int = 20
    log_level: str = "INFO"

    @property
    def trusted_host_list(self) -> list[str]:
        return [part.strip() for part in self.trusted_hosts.split(",") if part.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
