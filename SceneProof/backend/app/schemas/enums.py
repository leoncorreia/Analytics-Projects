from enum import StrEnum


class JobStatus(StrEnum):
    PENDING = "pending"
    REVIEWING = "reviewing"
    REVIEW_READY = "review_ready"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class AssetType(StrEnum):
    STORYBOARD = "storyboard"
    VIDEO = "video"
    AVATAR = "avatar"
    NARRATION = "narration"
    ASSEMBLED = "assembled"


class ValidationSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PipelineStage(StrEnum):
    INGESTION = "ingestion"
    EXTRACTION = "extraction"
    PLANNING = "planning"
    STORYBOARD = "storyboard"
    NARRATION = "narration"
    VIDEO = "video"
    AVATAR = "avatar"
    VALIDATION = "validation"
    ASSEMBLY = "assembly"
