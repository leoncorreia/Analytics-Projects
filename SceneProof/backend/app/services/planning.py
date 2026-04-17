import logging
import uuid
from typing import Any

from app.providers.seed2 import Seed2Provider
from app.schemas.citation import CitationReference
from app.schemas.document import ExtractedInsights
from app.schemas.enums import AssetType
from app.schemas.scene import Scene, ScenePlan

logger = logging.getLogger(__name__)


class PlanningService:
    def __init__(self, provider: Seed2Provider) -> None:
        self.provider = provider

    async def build_plan(
        self,
        *,
        source_text: str,
        insights: ExtractedInsights,
        audience: str,
        language: str,
        style_preset: str,
    ) -> ScenePlan:
        system = (
            "You are Seed 2.0 planning training scenes. "
            "Each scene must map to explicit source_support excerpts copied from SOURCE_TEXT."
        )
        user = (
            f"Audience: {audience}\nLanguage: {language}\nStyle: {style_preset}\n\n"
            f"INSIGHTS JSON:\n{insights.model_dump_json()}\n\n"
            f"SOURCE_TEXT:\n{source_text[:12000]}\n"
        )
        data: dict[str, Any] = await self.provider.structured_complete(
            system=system,
            user=user,
            response_label="scene_plan",
        )
        scenes_raw = list(data.get("scenes") or [])
        scenes: list[Scene] = []
        for raw in scenes_raw:
            cites: list[CitationReference] = []
            for c in raw.get("source_support") or []:
                cites.append(
                    CitationReference(
                        citation_id=str(c.get("citation_id") or f"cite_{uuid.uuid4().hex[:6]}"),
                        source_excerpt=str(c.get("source_excerpt") or "")[:800],
                        section_hint=c.get("section_hint"),
                        page_hint=c.get("page_hint"),
                        char_start=c.get("char_start"),
                        char_end=c.get("char_end"),
                    )
                )
            asset_raw = str(raw.get("asset_type") or "video").lower()
            try:
                asset_type = AssetType(asset_raw)
            except ValueError:
                asset_type = AssetType.VIDEO
            scenes.append(
                Scene(
                    scene_id=str(raw.get("scene_id") or f"scene_{uuid.uuid4().hex[:6]}"),
                    title=str(raw.get("title") or "Scene"),
                    objective=str(raw.get("objective") or ""),
                    narration=str(raw.get("narration") or ""),
                    visual_prompt=str(raw.get("visual_prompt") or ""),
                    asset_type=asset_type,
                    duration_estimate=float(raw.get("duration_estimate") or 8.0),
                    source_support=cites,
                    risk_flags=list(raw.get("risk_flags") or []),
                )
            )
        demo = self.provider.health().demo_mode
        return ScenePlan(
            plan_id=f"plan_{uuid.uuid4().hex[:10]}",
            scenes=scenes,
            audience=audience,
            language=language,
            style_preset=style_preset,
            demo_synthetic=demo,
        )
