import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import get_settings
from app.deps import get_job_store, get_orchestrator, get_seed2
from app.schemas.enums import JobStatus, PipelineStage
from app.schemas.job import Job, JobProgress
from app.schemas.result import GenerationResult
from app.services.ingestion import IngestionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", status_code=201)
async def create_job(
    audience: Annotated[str, Form()] = "General staff",
    language: Annotated[str, Form()] = "en",
    style_preset: Annotated[str, Form()] = "corporate",
    raw_text: Annotated[str | None, Form()] = None,
    document: UploadFile | None = File(None),
    presenter_image: UploadFile | None = File(None),
) -> Job:
    store = get_job_store()
    ingestion = IngestionService(store)

    normalized = (raw_text or "").strip()
    filename: str | None = None
    mime: str | None = None
    doc_bytes: bytes | None = None

    if document is not None:
        doc_bytes = await document.read()
        mime = document.content_type
        filename = document.filename or "upload"
        lower = (filename or "").lower()
        if mime == "application/pdf" or lower.endswith(".pdf"):
            normalized = ingestion.extract_text_from_pdf_bytes(doc_bytes)
        else:
            try:
                normalized = doc_bytes.decode("utf-8")
            except UnicodeDecodeError:
                normalized = doc_bytes.decode("utf-8", errors="ignore")

    if not normalized.strip():
        raise HTTPException(status_code=400, detail="Provide raw_text or a document upload.")

    job_id = store.new_job_id()
    source = await ingestion.build_source_document(
        job_id=job_id,
        normalized_text=normalized,
        filename=filename,
        mime_type=mime,
        language=language,
    )

    if doc_bytes is not None:
        await ingestion.persist_upload(job_id, filename or "upload", doc_bytes)

    presenter_path: str | None = None
    if presenter_image is not None:
        pdata = await presenter_image.read()
        ext = ".png"
        if presenter_image.filename and "." in presenter_image.filename:
            ext = "." + presenter_image.filename.rsplit(".", 1)[-1].lower()[:5]
        dest = await ingestion.persist_upload(job_id, f"presenter{ext}", pdata)
        presenter_path = f"jobs/{job_id}/uploads/{dest.name}"

    demo = bool(get_settings().demo_mode or get_seed2().health().demo_mode)
    job = Job(
        job_id=job_id,
        status=JobStatus.PENDING,
        audience=audience,
        language=language,
        style_preset=style_preset,
        presenter_image_path=presenter_path,
        source=source,
        result=GenerationResult(job_id=job_id, demo_mode=demo),
    )
    await store.init_job(job)
    logger.info("Created job %s", job_id)
    return job


@router.get("/{job_id}")
async def get_job(job_id: str) -> Job:
    store = get_job_store()
    job = await store.load(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/result")
async def get_result(job_id: str) -> GenerationResult:
    store = get_job_store()
    job = await store.load(job_id)
    if not job or not job.result:
        raise HTTPException(status_code=404, detail="Result not available")
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=409,
            detail=f"Job not completed (status={job.status}). Poll /api/jobs/{{id}}.",
        )
    return job.result


@router.post("/{job_id}/review")
async def run_review(job_id: str) -> Job:
    store = get_job_store()
    orch = get_orchestrator()
    job = await store.load(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in (JobStatus.REVIEWING, JobStatus.GENERATING):
        return job
    if job.status == JobStatus.REVIEW_READY:
        return job
    if job.status == JobStatus.COMPLETED:
        return job
    if job.status == JobStatus.FAILED:
        job.status = JobStatus.PENDING
        job.error = None
        job.progress = JobProgress(
            stage=PipelineStage.INGESTION, percent=0, message="Retrying review"
        )
        await store.save(job)
    if job.status == JobStatus.PENDING:
        job.status = JobStatus.REVIEWING
        job.progress = JobProgress(
            stage=PipelineStage.INGESTION,
            percent=1,
            message="Queued for review pipeline",
        )
        await store.save(job)
    orch.spawn_review(job_id)
    job = await store.load(job_id)
    assert job
    return job


@router.post("/{job_id}/generate")
async def run_generate(job_id: str) -> Job:
    store = get_job_store()
    orch = get_orchestrator()
    job = await store.load(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.REVIEW_READY:
        raise HTTPException(
            status_code=400,
            detail=f"Job must be review_ready (current={job.status}).",
        )
    job.status = JobStatus.GENERATING
    job.progress = JobProgress(
        stage=PipelineStage.STORYBOARD,
        percent=2,
        message="Queued for generation pipeline",
    )
    await store.save(job)
    orch.spawn_generate(job_id)
    job = await store.load(job_id)
    assert job
    return job


@router.post("/{job_id}/regenerate-scene/{scene_id}")
async def regenerate_scene(job_id: str, scene_id: str) -> dict:
    store = get_job_store()
    job = await store.load(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    logger.info("Regenerate scene placeholder job=%s scene=%s", job_id, scene_id)
    return {
        "job_id": job_id,
        "scene_id": scene_id,
        "status": "queued",
        "message": "Per-scene regeneration is not yet implemented; pipeline hook reserved.",
        "demo": True,
    }
