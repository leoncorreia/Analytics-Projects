from pydantic import BaseModel, Field


class CitationReference(BaseModel):
    citation_id: str = Field(..., description="Stable id for UI linking")
    source_excerpt: str = Field(..., description="Quoted or paraphrased support from source")
    section_hint: str | None = Field(None, description="Section or heading if known")
    page_hint: int | None = Field(None, description="Approximate page for PDF sources")
    char_start: int | None = None
    char_end: int | None = None
