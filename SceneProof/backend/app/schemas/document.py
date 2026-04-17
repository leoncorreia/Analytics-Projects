from pydantic import BaseModel, Field

from app.schemas.enums import AssetType


class SourceDocument(BaseModel):
    document_id: str
    filename: str | None = None
    mime_type: str | None = None
    normalized_text: str
    sections: list[str] = Field(default_factory=list)
    language: str = "en"
    char_count: int = 0


class ExtractedInsights(BaseModel):
    goals: list[str] = Field(default_factory=list)
    required_steps: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    forbidden_claims: list[str] = Field(default_factory=list)
    key_entities: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    summary: str | None = None
    demo_synthetic: bool = Field(
        default=False, description="True when insights were generated in demo/mock mode"
    )


class MediaAsset(BaseModel):
    asset_id: str
    scene_id: str | None = None
    asset_type: AssetType
    uri: str = Field(..., description="Relative path under job storage or URL")
    mime_type: str | None = None
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None
    provider: str = "mock"
    demo_placeholder: bool = False
