import json
import logging
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.providers.base import ProviderHealth

logger = logging.getLogger(__name__)


class Seed2Provider:
    """Seed 2.0 — reasoning, extraction, planning, validation prompts."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._demo = self.settings.demo_mode or not (
            self.settings.seed2_api_key and self.settings.seed2_base_url
        )

    def health(self) -> ProviderHealth:
        configured = bool(self.settings.seed2_api_key and self.settings.seed2_base_url)
        return ProviderHealth(name="seed2", configured=configured, demo_mode=self._demo)

    async def structured_complete(
        self, *, system: str, user: str, response_label: str
    ) -> dict[str, Any]:
        if self._demo:
            return self._mock_structured(user, response_label)

        assert self.settings.seed2_base_url and self.settings.seed2_api_key
        url = self.settings.seed2_base_url.rstrip("/") + "/v1/chat/completions"
        payload = {
            "model": self.settings.seed2_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.settings.seed2_api_key}"}
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Seed2 live call failed (%s); using mock.", exc)
            return self._mock_structured(user, response_label)

    def _mock_structured(self, user: str, label: str) -> dict[str, Any]:
        """Deterministic demo JSON shaped like production contracts."""
        lines = [ln.strip() for ln in user.splitlines() if ln.strip()]
        snippet = " ".join(lines[:3])[:400]
        if label == "extraction":
            return {
                "goals": ["Communicate policy clearly", "Reduce operational risk"],
                "required_steps": [
                    "Review the source document",
                    "Apply steps in order",
                    "Document exceptions",
                ],
                "constraints": ["Do not contradict the source text", "Call out uncertainty"],
                "forbidden_claims": ["Guaranteed outcomes not stated in source"],
                "key_entities": ["Policy owner", "Audience", "Compliance"],
                "warnings": ["Demo mode: verify against original PDF"],
                "summary": snippet or "Demo summary generated from your input.",
            }
        if label == "scene_plan":
            return {
                "scenes": [
                    {
                        "scene_id": "scene_intro",
                        "title": "Introduction",
                        "objective": "Orient the audience and state scope",
                        "narration": "Welcome. This training reflects the uploaded policy. "
                        "We will walk through the essentials step by step.",
                        "visual_prompt": "Modern office, soft lighting, inclusive team reviewing a document",
                        "asset_type": "video",
                        "duration_estimate": 10,
                        "source_support": [
                            {
                                "citation_id": "cit_intro",
                                "source_excerpt": snippet[:200] or "Source document",
                                "section_hint": "Overview",
                                "page_hint": 1,
                            }
                        ],
                        "risk_flags": [],
                    },
                    {
                        "scene_id": "scene_steps",
                        "title": "Required steps",
                        "objective": "Teach the mandatory sequence",
                        "narration": "Follow these steps exactly as written. "
                        "If a step conflicts with local law, escalate before proceeding.",
                        "visual_prompt": "Checklist on screen, calm narrator tone, crisp typography",
                        "asset_type": "video",
                        "duration_estimate": 18,
                        "source_support": [
                            {
                                "citation_id": "cit_steps",
                                "source_excerpt": snippet[200:400] if len(snippet) > 200 else snippet,
                                "section_hint": "Procedure",
                                "page_hint": 2,
                            }
                        ],
                        "risk_flags": ["verify_numbers"],
                    },
                    {
                        "scene_id": "scene_close",
                        "title": "Recap and compliance",
                        "objective": "Reinforce constraints and next actions",
                        "narration": "Remember the constraints we highlighted. "
                        "When in doubt, cite the policy and ask for clarification.",
                        "visual_prompt": "Closing frame with logo placeholder, confident presenter silhouette",
                        "asset_type": "video",
                        "duration_estimate": 12,
                        "source_support": [
                            {
                                "citation_id": "cit_close",
                                "source_excerpt": snippet[-200:] if snippet else "Source document",
                                "section_hint": "Closing",
                                "page_hint": 3,
                            }
                        ],
                        "risk_flags": [],
                    },
                ]
            }
        if label == "validation":
            return {
                "issues": [
                    {
                        "issue_id": "val_demo",
                        "scene_id": "scene_steps",
                        "severity": "warning",
                        "code": "UNSUPPORTED_DETAIL",
                        "message": "Demo validation: confirm numeric thresholds against source.",
                        "suggested_fix": "Replace with values explicitly present in the PDF.",
                    }
                ]
            }
        logger.debug("Seed2 mock: no template for label=%s", label)
        return {}
