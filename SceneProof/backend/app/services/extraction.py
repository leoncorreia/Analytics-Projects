import logging
from typing import Any

from app.providers.seed2 import Seed2Provider
from app.schemas.document import ExtractedInsights

logger = logging.getLogger(__name__)


class ExtractionService:
    def __init__(self, provider: Seed2Provider) -> None:
        self.provider = provider

    async def extract(self, *, source_text: str, audience: str, language: str) -> ExtractedInsights:
        system = (
            "You are Seed 2.0 assisting compliance trainers. "
            "Return strict JSON matching the requested schema. "
            "Never invent citations; if unsure, add warnings."
        )
        user = (
            f"Audience: {audience}\nLanguage: {language}\n\n"
            f"SOURCE_TEXT:\n{source_text[:12000]}\n"
        )
        data: dict[str, Any] = await self.provider.structured_complete(
            system=system,
            user=user,
            response_label="extraction",
        )
        demo = self.provider.health().demo_mode
        return ExtractedInsights(
            goals=list(data.get("goals") or []),
            required_steps=list(data.get("required_steps") or []),
            constraints=list(data.get("constraints") or []),
            forbidden_claims=list(data.get("forbidden_claims") or []),
            key_entities=list(data.get("key_entities") or []),
            warnings=list(data.get("warnings") or []),
            summary=str(data.get("summary") or "")[:2000] or None,
            demo_synthetic=demo,
        )
