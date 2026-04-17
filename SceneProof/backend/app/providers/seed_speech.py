import logging
import uuid
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.providers.base import ProviderHealth

logger = logging.getLogger(__name__)


class SeedSpeechProvider:
    """Seed Speech — narration / TTS."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._demo = self.settings.demo_mode or not (
            self.settings.seed_speech_api_key and self.settings.seed_speech_base_url
        )

    def health(self) -> ProviderHealth:
        configured = bool(
            self.settings.seed_speech_api_key and self.settings.seed_speech_base_url
        )
        return ProviderHealth(name="seed_speech", configured=configured, demo_mode=self._demo)

    async def synthesize(
        self,
        *,
        text: str,
        job_id: str,
        scene_id: str | None,
        language: str = "en",
    ) -> dict[str, Any]:
        if self._demo:
            sid = scene_id or "global"
            return {
                "asset_id": f"narr_{uuid.uuid4().hex[:8]}",
                "relative_path": f"jobs/{job_id}/assets/narration_{sid}.wav",
                "mime_type": "audio/wav",
                "duration_seconds": max(3.0, min(60.0, len(text) / 14)),
                "provider": "seed_speech-mock",
                "demo_placeholder": True,
            }

        assert self.settings.seed_speech_base_url and self.settings.seed_speech_api_key
        url = self.settings.seed_speech_base_url.rstrip("/") + "/v1/audio/speech"
        payload = {
            "model": self.settings.seed_speech_model,
            "input": text,
            "language": language,
        }
        headers = {"Authorization": f"Bearer {self.settings.seed_speech_api_key}"}
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
            return {
                "asset_id": f"narr_{uuid.uuid4().hex[:8]}",
                "relative_path": f"jobs/{job_id}/assets/narration_{scene_id or 'global'}.wav",
                "mime_type": "audio/wav",
                "duration_seconds": max(3.0, min(120.0, len(text) / 14)),
                "provider": "seed_speech",
                "demo_placeholder": False,
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Seed Speech live call failed (%s); using placeholder metadata.", exc)
            return {
                "asset_id": f"narr_{uuid.uuid4().hex[:8]}",
                "relative_path": f"jobs/{job_id}/assets/narration_{scene_id or 'global'}.wav",
                "mime_type": "audio/wav",
                "duration_seconds": max(3.0, min(60.0, len(text) / 14)),
                "provider": "seed_speech-fallback",
                "demo_placeholder": True,
            }
