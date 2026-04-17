import logging
import uuid
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.providers.base import ProviderHealth

logger = logging.getLogger(__name__)


class SeedreamProvider:
    """Seedream 5.0 — storyboard / keyframe images."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._demo = self.settings.demo_mode or not (
            self.settings.seedream_api_key and self.settings.seedream_base_url
        )

    def health(self) -> ProviderHealth:
        configured = bool(self.settings.seedream_api_key and self.settings.seedream_base_url)
        return ProviderHealth(name="seedream", configured=configured, demo_mode=self._demo)

    async def generate_image(
        self,
        *,
        prompt: str,
        job_id: str,
        scene_id: str,
        width: int = 1024,
        height: int = 576,
    ) -> dict[str, Any]:
        if self._demo:
            return {
                "asset_id": f"sb_{uuid.uuid4().hex[:8]}",
                "relative_path": f"jobs/{job_id}/assets/storyboard_{scene_id}.png",
                "mime_type": "image/png",
                "provider": "seedream-mock",
                "demo_placeholder": True,
                "prompt": prompt,
            }

        assert self.settings.seedream_base_url and self.settings.seedream_api_key
        url = self.settings.seedream_base_url.rstrip("/") + "/v1/images/generations"
        payload = {
            "model": self.settings.seedream_model,
            "prompt": prompt,
            "size": f"{width}x{height}",
        }
        headers = {"Authorization": f"Bearer {self.settings.seedream_api_key}"}
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            # Normalized contract — adjust when live API schema is known
            image_url = data["data"][0]["url"]
            return {
                "asset_id": f"sb_{uuid.uuid4().hex[:8]}",
                "remote_url": image_url,
                "mime_type": "image/png",
                "provider": "seedream",
                "demo_placeholder": False,
                "prompt": prompt,
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("Seedream live call failed (%s); using placeholder metadata.", exc)
            return {
                "asset_id": f"sb_{uuid.uuid4().hex[:8]}",
                "relative_path": f"jobs/{job_id}/assets/storyboard_{scene_id}.png",
                "mime_type": "image/png",
                "provider": "seedream-fallback",
                "demo_placeholder": True,
                "prompt": prompt,
            }
