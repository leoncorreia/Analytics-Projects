from pydantic import BaseModel, Field

from app.schemas.enums import ValidationSeverity


class ValidationIssue(BaseModel):
    issue_id: str
    scene_id: str | None = None
    severity: ValidationSeverity = ValidationSeverity.WARNING
    code: str
    message: str
    suggested_fix: str | None = None
