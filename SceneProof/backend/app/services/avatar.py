import logging

from app.providers.omnihuman import OmniHumanProvider
from app.schemas.document import MediaAsset
from app.schemas.enums import AssetType

logger = logging.getLogger(__name__)


class AvatarService:
    def __init__(self, provider: OmniHumanProvider) -> None:
        self.provider = provider

    async def maybe_generate(
        self, *, job_id: str, presenter_image_path: str | None, intro_script: str
    ) -> list[MediaAsset]:
        if not presenter_image_path:
            return []
        meta = await self.provider.generate_presenter_clip(
            presenter_image_path=presenter_image_path,
            script=intro_script,
            job_id=job_id,
        )
        asset = MediaAsset(
            asset_id=meta["asset_id"],
            scene_id=None,
            asset_type=AssetType.AVATAR,
            uri=meta.get("relative_path") or meta.get("remote_url") or "",
            mime_type=meta.get("mime_type"),
            duration_seconds=float(meta.get("duration_seconds") or 0),
            provider=str(meta.get("provider")),
            demo_placeholder=bool(meta.get("demo_placeholder")),
        )
        logger.info("Presenter clip metadata created for job %s", job_id)
        return [asset]
