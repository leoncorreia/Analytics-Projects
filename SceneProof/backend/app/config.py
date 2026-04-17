from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> backend/ is the package root for local runs
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(_REPO_ROOT / ".env"),
            str(_BACKEND_ROOT / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SceneProof API"
    debug: bool = False
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    data_dir: str = "./data"

    seed2_api_key: str | None = None
    seed2_base_url: str | None = None
    seed2_model: str = "seed-2.0"

    seedream_api_key: str | None = None
    seedream_base_url: str | None = None
    seedream_model: str = "seedream-5.0"

    seedance_api_key: str | None = None
    seedance_base_url: str | None = None
    seedance_model: str = "seedance-2.0"

    seed_speech_api_key: str | None = None
    seed_speech_base_url: str | None = None
    seed_speech_model: str = "seed-speech"

    omnihuman_api_key: str | None = None
    omnihuman_base_url: str | None = None
    omnihuman_model: str = "omnihuman"

    demo_mode: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
