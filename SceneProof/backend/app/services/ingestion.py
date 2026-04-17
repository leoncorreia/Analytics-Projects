import logging
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from app.schemas.document import SourceDocument
from app.storage.job_store import JobStore

logger = logging.getLogger(__name__)


def _split_sections(text: str, max_sections: int = 12) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []
    for line in text.splitlines():
        if line.strip().startswith("#") or (
            line.isupper() and len(line.strip()) > 3 and len(line.split()) <= 8
        ):
            if buf:
                chunks.append("\n".join(buf).strip())
                buf = []
        buf.append(line)
    if buf:
        chunks.append("\n".join(buf).strip())
    chunks = [c for c in chunks if c]
    if len(chunks) <= 1:
        # fallback: split by double newline
        chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
    return chunks[:max_sections] if chunks else [text.strip()[:4000]]


class IngestionService:
    def __init__(self, store: JobStore) -> None:
        self.store = store

    async def build_source_document(
        self,
        *,
        job_id: str,
        normalized_text: str,
        filename: str | None,
        mime_type: str | None,
        language: str,
    ) -> SourceDocument:
        sections = _split_sections(normalized_text)
        doc = SourceDocument(
            document_id=f"doc_{job_id}",
            filename=filename,
            mime_type=mime_type,
            normalized_text=normalized_text,
            sections=sections,
            language=language,
            char_count=len(normalized_text),
        )
        logger.info("Ingested document for job %s (%s chars)", job_id, doc.char_count)
        return doc

    def extract_text_from_pdf_bytes(self, data: bytes, max_pages: int = 40) -> str:
        reader = PdfReader(BytesIO(data))
        texts: list[str] = []
        for i, page in enumerate(reader.pages[:max_pages]):
            try:
                texts.append(page.extract_text() or "")
            except Exception as exc:  # noqa: BLE001
                logger.warning("PDF page %s extract failed: %s", i, exc)
        joined = "\n\n".join(t for t in texts if t.strip())
        return joined.strip() or "Unable to extract text from PDF; paste content instead."

    async def persist_upload(self, job_id: str, filename: str, data: bytes) -> Path:
        dest_dir = self.store.uploads_dir(job_id)
        safe_name = filename.replace("..", "_").replace("/", "_")
        path = dest_dir / safe_name
        path.write_bytes(data)
        return path
