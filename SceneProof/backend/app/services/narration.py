import logging

from app.providers.seed_speech import SeedSpeechProvider
from app.schemas.document import MediaAsset
from app.schemas.enums import AssetType
from app.schemas.media_tracks import NarrationTrack
from app.schemas.scene import ScenePlan

logger = logging.getLogger(__name__)


class NarrationService:
    def __init__(self, provider: SeedSpeechProvider) -> None:
        self.provider = provider

    async def synthesize_plan(
        self, *, job_id: str, plan: ScenePlan, language: str
    ) -> tuple[list[NarrationTrack], list[MediaAsset]]:
        tracks: list[NarrationTrack] = []
        assets: list[MediaAsset] = []
        for scene in plan.scenes:
            meta = await self.provider.synthesize(
                text=scene.narration,
                job_id=job_id,
                scene_id=scene.scene_id,
                language=language,
            )
            asset = MediaAsset(
                asset_id=meta["asset_id"],
                scene_id=scene.scene_id,
                asset_type=AssetType.NARRATION,
                uri=meta.get("relative_path") or meta.get("remote_url") or "",
                mime_type=meta.get("mime_type"),
                duration_seconds=float(meta.get("duration_seconds") or 0),
                provider=str(meta.get("provider")),
                demo_placeholder=bool(meta.get("demo_placeholder")),
            )
            assets.append(asset)
            tracks.append(
                NarrationTrack(
                    track_id=f"trk_{scene.scene_id}",
                    scene_id=scene.scene_id,
                    text=scene.narration,
                    audio_asset_id=asset.asset_id,
                    language=language,
                )
            )
        logger.info("Narration synthesized for job %s (%s tracks)", job_id, len(tracks))
        return tracks, assets
