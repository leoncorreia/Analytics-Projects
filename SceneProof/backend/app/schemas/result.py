from pydantic import BaseModel, Field

from app.schemas.document import MediaAsset
from app.schemas.media_tracks import NarrationTrack, StoryboardFrame
from app.schemas.scene import ScenePlan
from app.schemas.validation import ValidationIssue


class AssemblyManifest(BaseModel):
    """Describes how final media would be stitched; demo uses metadata-only assembly."""

    final_video_asset_id: str | None = None
    subtitle_asset_id: str | None = None
    transcript_text: str = ""
    chapters: list[dict] = Field(default_factory=list)


class GenerationResult(BaseModel):
    job_id: str
    scene_plan: ScenePlan | None = None
    storyboard_frames: list[StoryboardFrame] = Field(default_factory=list)
    narration_tracks: list[NarrationTrack] = Field(default_factory=list)
    media_assets: list[MediaAsset] = Field(default_factory=list)
    validation_issues: list[ValidationIssue] = Field(default_factory=list)
    assembly: AssemblyManifest | None = None
    demo_mode: bool = False
