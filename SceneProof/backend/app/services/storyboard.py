import logging

from app.providers.seedream import SeedreamProvider
from app.schemas.document import MediaAsset
from app.schemas.enums import AssetType
from app.schemas.media_tracks import StoryboardFrame
from app.schemas.scene import ScenePlan

logger = logging.getLogger(__name__)


class StoryboardService:
    def __init__(self, provider: SeedreamProvider) -> None:
        self.provider = provider

    async def generate_frames(
        self, *, job_id: str, plan: ScenePlan
    ) -> tuple[list[StoryboardFrame], list[MediaAsset]]:
        frames: list[StoryboardFrame] = []
        assets: list[MediaAsset] = []
        order = 0
        for scene in plan.scenes:
            meta = await self.provider.generate_image(
                prompt=scene.visual_prompt,
                job_id=job_id,
                scene_id=scene.scene_id,
            )
            asset = MediaAsset(
                asset_id=meta["asset_id"],
                scene_id=scene.scene_id,
                asset_type=AssetType.STORYBOARD,
                uri=meta.get("relative_path")
                or meta.get("remote_url")
                or f"jobs/{job_id}/assets/storyboard_{scene.scene_id}.png",
                mime_type=meta.get("mime_type"),
                provider=str(meta.get("provider")),
                demo_placeholder=bool(meta.get("demo_placeholder")),
            )
            assets.append(asset)
            frames.append(
                StoryboardFrame(
                    frame_id=f"frm_{scene.scene_id}",
                    scene_id=scene.scene_id,
                    image_asset_id=asset.asset_id,
                    prompt_used=str(meta.get("prompt") or scene.visual_prompt),
                    order=order,
                )
            )
            order += 1
        logger.info("Storyboard frames generated for job %s (%s)", job_id, len(frames))
        return frames, assets
