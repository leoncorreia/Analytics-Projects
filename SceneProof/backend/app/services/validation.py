import logging
import uuid
from typing import Any

from app.providers.seed2 import Seed2Provider
from app.schemas.enums import ValidationSeverity
from app.schemas.scene import ScenePlan
from app.schemas.validation import ValidationIssue

logger = logging.getLogger(__name__)


class ValidationService:
    def __init__(self, provider: Seed2Provider) -> None:
        self.provider = provider

    async def validate_plan(
        self, *, source_text: str, plan: ScenePlan
    ) -> list[ValidationIssue]:
        system = (
            "You are Seed 2.0 validating training scripts against source policy. "
            "Flag unsupported claims, missing disclaimers, or risky language."
        )
        user = (
            f"SOURCE_TEXT:\n{source_text[:12000]}\n\n"
            f"SCENE_PLAN_JSON:\n{plan.model_dump_json()}\n"
        )
        data: dict[str, Any] = await self.provider.structured_complete(
            system=system,
            user=user,
            response_label="validation",
        )
        issues: list[ValidationIssue] = []
        for raw in data.get("issues") or []:
            sev_raw = str(raw.get("severity") or "warning").lower()
            try:
                severity = ValidationSeverity(sev_raw)
            except ValueError:
                severity = ValidationSeverity.WARNING
            issues.append(
                ValidationIssue(
                    issue_id=str(raw.get("issue_id") or f"iss_{uuid.uuid4().hex[:6]}"),
                    scene_id=raw.get("scene_id"),
                    severity=severity,
                    code=str(raw.get("code") or "GENERIC"),
                    message=str(raw.get("message") or ""),
                    suggested_fix=raw.get("suggested_fix"),
                )
            )
        issues.extend(self._heuristic_checks(source_text, plan))
        logger.info("Validation produced %s issues for plan %s", len(issues), plan.plan_id)
        return issues

    def _heuristic_checks(self, source_text: str, plan: ScenePlan) -> list[ValidationIssue]:
        lowered = source_text.lower()
        found: list[ValidationIssue] = []
        risky_terms = ["guarantee", "always safe", "cannot fail"]
        for scene in plan.scenes:
            narr = scene.narration.lower()
            for term in risky_terms:
                if term in narr and term not in lowered:
                    found.append(
                        ValidationIssue(
                            issue_id=f"heur_{scene.scene_id}_{term}",
                            scene_id=scene.scene_id,
                            severity=ValidationSeverity.WARNING,
                            code="STRONG_CLAIM",
                            message=f"Narration contains '{term}' which is not found verbatim in source.",
                            suggested_fix="Soften language or cite explicit policy language.",
                        )
                    )
        return found
