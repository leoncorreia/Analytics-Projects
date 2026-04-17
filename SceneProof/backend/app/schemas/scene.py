from pydantic import BaseModel, Field

from app.schemas.citation import CitationReference
from app.schemas.enums import AssetType


class Scene(BaseModel):
    scene_id: str
    title: str
    objective: str
    narration: str
    visual_prompt: str
    asset_type: AssetType = AssetType.VIDEO
    duration_estimate: float = Field(8.0, description="Estimated seconds")
    source_support: list[CitationReference] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


class ScenePlan(BaseModel):
    plan_id: str
    scenes: list[Scene] = Field(default_factory=list)
    audience: str = ""
    language: str = "en"
    style_preset: str = "corporate"
    demo_synthetic: bool = False
