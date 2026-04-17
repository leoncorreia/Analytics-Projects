from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

from app.schemas.document import ExtractedInsights, SourceDocument
from app.schemas.enums import JobStatus, PipelineStage
from app.schemas.result import GenerationResult


class JobProgress(BaseModel):
    stage: PipelineStage | str = PipelineStage.INGESTION
    percent: float = 0.0
    message: str = ""


class Job(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
    audience: str = "General audience"
    language: str = "en"
    style_preset: str = "corporate"
    presenter_image_path: str | None = None
    source: SourceDocument | None = None
    insights: ExtractedInsights | None = None
    progress: JobProgress = Field(default_factory=JobProgress)
    error: str | None = None
    result: GenerationResult | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
