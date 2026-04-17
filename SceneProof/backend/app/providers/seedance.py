import logging
import uuid
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.providers.base import ProviderHealth

logger = logging.getLogger(__name__)


class SeedanceProvider:
    """Seedance 2.0 — per-scene video generation."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._demo = self.settings.demo_mode or not (
            self.settings.seedance_api_key and self.settings.seedance_base_url
        )

    def health(self) -> ProviderHealth:
        configured = bool(self.settings.seedance_api_key and self.settings.seedance_base_url)
        return ProviderHealth(name="seedance", configured=configured, demo_mode=self._demo)

    async def generate_scene_video(
        self,
        *,
        prompt: str,
        job_id: str,
        scene_id: str,
        duration_seconds: float = 8.0,
    ) -> dict[str, Any]:
        if self._demo:
            return {
                "asset_id": f"vid_{uuid.uuid4().hex[:8]}",
                "relative_path": f"jobs/{job_id}/assets/video_{scene_id}.mp4",
                "mime_type": "video/mp4",
                "duration_seconds": duration_seconds,
                "provider": "seedance-mock",
                "demo_placeholder": True,
                "prompt": prompt,
            }

        assert self.settings.seedance_base_url and self.settings.seedance_api_key
        url = self.settings.seedance_base_url.rstrip("/") + "/v1/videos/generations"
        payload = {
            "model": self.settings.seedance_model,
            "prompt": prompt,
            "duration": duration_seconds,
        }
        headers = {"Authorization": f"Bearer {self.settings.seedance_api_key}"}
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            return {
                "asset_id": f"vid_{uuid.uuid4().hex[:8]}",
                "remote_url": data.get("url") or data.get("output_url"),
                "mime_type": "video/mp4",
                "duration_seconds": duration_seconds,
                "provider": "seedance",
                "demo_placeholder": False,
                "prompt": prompt,
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Seedance live call failed (%s); using placeholder metadata.", exc)
            return {
                "asset_id": f"vid_{uuid.uuid4().hex[:8]}",
                "relative_path": f"jobs/{job_id}/assets/video_{scene_id}.mp4",
                "mime_type": "video/mp4",
                "duration_seconds": duration_seconds,
                "provider": "seedance-fallback",
                "demo_placeholder": True,
                "prompt": prompt,
            }
