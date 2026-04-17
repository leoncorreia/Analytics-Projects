import logging
import uuid
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.providers.base import ProviderHealth

logger = logging.getLogger(__name__)


class OmniHumanProvider:
    """OmniHuman — presenter avatar clips."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._demo = self.settings.demo_mode or not (
            self.settings.omnihuman_api_key and self.settings.omnihuman_base_url
        )

    def health(self) -> ProviderHealth:
        configured = bool(self.settings.omnihuman_api_key and self.settings.omnihuman_base_url)
        return ProviderHealth(name="omnihuman", configured=configured, demo_mode=self._demo)

    async def generate_presenter_clip(
        self,
        *,
        presenter_image_path: str,
        script: str,
        job_id: str,
    ) -> dict[str, Any]:
        if self._demo:
            return {
                "asset_id": f"av_{uuid.uuid4().hex[:8]}",
                "relative_path": f"jobs/{job_id}/assets/presenter_intro.mp4",
                "mime_type": "video/mp4",
                "duration_seconds": 6.0,
                "provider": "omnihuman-mock",
                "demo_placeholder": True,
            }

        assert self.settings.omnihuman_base_url and self.settings.omnihuman_api_key
        url = self.settings.omnihuman_base_url.rstrip("/") + "/v1/avatar/render"
        payload = {
            "model": self.settings.omnihuman_model,
            "image_uri": presenter_image_path,
            "script": script,
        }
        headers = {"Authorization": f"Bearer {self.settings.omnihuman_api_key}"}
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            return {
                "asset_id": f"av_{uuid.uuid4().hex[:8]}",
                "remote_url": data.get("url"),
                "mime_type": "video/mp4",
                "duration_seconds": float(data.get("duration", 6.0)),
                "provider": "omnihuman",
                "demo_placeholder": False,
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("OmniHuman live call failed (%s); using placeholder metadata.", exc)
            return {
                "asset_id": f"av_{uuid.uuid4().hex[:8]}",
                "relative_path": f"jobs/{job_id}/assets/presenter_intro.mp4",
                "mime_type": "video/mp4",
                "duration_seconds": 6.0,
                "provider": "omnihuman-fallback",
                "demo_placeholder": True,
            }
