import logging

from app.providers.seedance import SeedanceProvider
from app.schemas.document import MediaAsset
from app.schemas.enums import AssetType
from app.schemas.scene import ScenePlan

logger = logging.getLogger(__name__)


class VideoGenerationService:
    def __init__(self, provider: SeedanceProvider) -> None:
        self.provider = provider

    async def generate_videos(self, *, job_id: str, plan: ScenePlan) -> list[MediaAsset]:
        assets: list[MediaAsset] = []
        for scene in plan.scenes:
            meta = await self.provider.generate_scene_video(
                prompt=scene.visual_prompt + " | " + scene.objective,
                job_id=job_id,
                scene_id=scene.scene_id,
                duration_seconds=float(scene.duration_estimate or 8.0),
            )
            assets.append(
                MediaAsset(
                    asset_id=meta["asset_id"],
                    scene_id=scene.scene_id,
                    asset_type=AssetType.VIDEO,
                    uri=meta.get("relative_path") or meta.get("remote_url") or "",
                    mime_type=meta.get("mime_type"),
                    duration_seconds=float(meta.get("duration_seconds") or 0),
                    provider=str(meta.get("provider")),
                    demo_placeholder=bool(meta.get("demo_placeholder")),
                )
            )
        logger.info("Scene videos queued/generated for job %s (%s)", job_id, len(assets))
        return assets
