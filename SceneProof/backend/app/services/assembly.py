import logging
import uuid

from app.schemas.document import MediaAsset
from app.schemas.enums import AssetType
from app.schemas.media_tracks import NarrationTrack, StoryboardFrame
from app.schemas.result import AssemblyManifest, GenerationResult
from app.schemas.scene import ScenePlan
from app.schemas.validation import ValidationIssue

logger = logging.getLogger(__name__)


class AssemblyService:
    """Combines metadata for final packaging; binary stitching is delegated to future workers."""

    def build_result(
        self,
        *,
        job_id: str,
        plan: ScenePlan,
        storyboard_frames: list[StoryboardFrame],
        narration_tracks: list[NarrationTrack],
        media_assets: list[MediaAsset],
        validation_issues: list[ValidationIssue],
        demo_mode: bool,
    ) -> GenerationResult:
        transcript = "\n\n".join(
            f"## {scene.title}\n{scene.narration}" for scene in plan.scenes
        )
        chapters = [
            {"scene_id": s.scene_id, "title": s.title, "duration_estimate": s.duration_estimate}
            for s in plan.scenes
        ]
        final_asset = MediaAsset(
            asset_id=f"final_{uuid.uuid4().hex[:8]}",
            scene_id=None,
            asset_type=AssetType.ASSEMBLED,
            uri=f"jobs/{job_id}/exports/final_program.json",
            mime_type="application/json",
            duration_seconds=sum(s.duration_estimate for s in plan.scenes),
            provider="local-assembler",
            demo_placeholder=True,
        )
        manifest = AssemblyManifest(
            final_video_asset_id=final_asset.asset_id,
            subtitle_asset_id=None,
            transcript_text=transcript,
            chapters=chapters,
        )
        all_assets = [*media_assets, final_asset]
        logger.info("Assembled generation result for job %s", job_id)
        return GenerationResult(
            job_id=job_id,
            scene_plan=plan,
            storyboard_frames=storyboard_frames,
            narration_tracks=narration_tracks,
            media_assets=all_assets,
            validation_issues=validation_issues,
            assembly=manifest,
            demo_mode=demo_mode,
        )
