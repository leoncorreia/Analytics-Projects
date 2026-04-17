import asyncio
import logging
from typing import Any

from app.config import Settings, get_settings
from app.schemas.enums import JobStatus, PipelineStage
from app.schemas.job import Job, JobProgress
from app.schemas.result import GenerationResult
from app.services.assembly import AssemblyService
from app.services.avatar import AvatarService
from app.services.extraction import ExtractionService
from app.services.ingestion import IngestionService
from app.services.narration import NarrationService
from app.services.planning import PlanningService
from app.services.storyboard import StoryboardService
from app.services.validation import ValidationService
from app.services.video_generation import VideoGenerationService
from app.storage.job_store import JobStore

logger = logging.getLogger(__name__)


class JobOrchestrator:
    def __init__(
        self,
        store: JobStore,
        ingestion: IngestionService,
        extraction: ExtractionService,
        planning: PlanningService,
        storyboard: StoryboardService,
        narration: NarrationService,
        video_generation: VideoGenerationService,
        avatar: AvatarService,
        validation: ValidationService,
        assembly: AssemblyService,
        settings: Settings | None = None,
    ) -> None:
        self.store = store
        self.ingestion = ingestion
        self.extraction = extraction
        self.planning = planning
        self.storyboard = storyboard
        self.narration = narration
        self.video_generation = video_generation
        self.avatar = avatar
        self.validation = validation
        self.assembly = assembly
        self.settings = settings or get_settings()
        self._locks: dict[str, asyncio.Lock] = {}
        self._tasks: dict[str, asyncio.Task[Any]] = {}

    def _lock(self, job_id: str) -> asyncio.Lock:
        if job_id not in self._locks:
            self._locks[job_id] = asyncio.Lock()
        return self._locks[job_id]

    async def _update(
        self, job: Job, *, status: JobStatus | None = None, progress: JobProgress | None = None
    ) -> None:
        if status:
            job.status = status
        if progress:
            job.progress = progress
        await self.store.save(job)

    async def run_review_pipeline(self, job_id: str) -> None:
        lock = self._lock(job_id)
        async with lock:
            job = await self.store.load(job_id)
            if not job:
                return
            try:
                await self._update(
                    job,
                    status=JobStatus.REVIEWING,
                    progress=JobProgress(
                        stage=PipelineStage.INGESTION, percent=2, message="Normalizing source"
                    ),
                )
                assert job.source is not None
                await self._update(
                    job,
                    progress=JobProgress(
                        stage=PipelineStage.EXTRACTION,
                        percent=15,
                        message="Extracting policy insights (Seed 2.0)",
                    ),
                )
                insights = await self.extraction.extract(
                    source_text=job.source.normalized_text,
                    audience=job.audience,
                    language=job.language,
                )
                job.insights = insights
                await self.store.save(job)

                await self._update(
                    job,
                    progress=JobProgress(
                        stage=PipelineStage.PLANNING,
                        percent=35,
                        message="Building scene plan (Seed 2.0)",
                    ),
                )
                plan = await self.planning.build_plan(
                    source_text=job.source.normalized_text,
                    insights=insights,
                    audience=job.audience,
                    language=job.language,
                    style_preset=job.style_preset,
                )
                any_demo = self.settings.demo_mode or self.extraction.provider.health().demo_mode
                job.result = GenerationResult(
                    job_id=job.job_id,
                    scene_plan=plan,
                    demo_mode=any_demo,
                )
                await self._update(
                    job,
                    status=JobStatus.REVIEW_READY,
                    progress=JobProgress(
                        stage=PipelineStage.PLANNING,
                        percent=100,
                        message="Review ready — confirm and generate",
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("Review pipeline failed for %s", job_id)
                job.status = JobStatus.FAILED
                job.error = str(exc)
                job.progress = JobProgress(
                    stage=PipelineStage.PLANNING, percent=100, message="Failed during review"
                )
                await self.store.save(job)

    async def run_generation_pipeline(self, job_id: str) -> None:
        lock = self._lock(job_id)
        async with lock:
            job = await self.store.load(job_id)
            if not job or not job.result or not job.result.scene_plan or not job.source:
                return
            if job.status == JobStatus.COMPLETED:
                logger.info("Skipping generation for job %s (already completed)", job_id)
                return
            plan = job.result.scene_plan
            demo_mode = self.settings.demo_mode
            try:
                await self._update(
                    job,
                    status=JobStatus.GENERATING,
                    progress=JobProgress(
                        stage=PipelineStage.STORYBOARD,
                        percent=10,
                        message="Generating storyboard frames (Seedream 5.0)",
                    ),
                )
                frames, sb_assets = await self.storyboard.generate_frames(job_id=job_id, plan=plan)
                await self._update(
                    job,
                    progress=JobProgress(
                        stage=PipelineStage.NARRATION,
                        percent=35,
                        message="Synthesizing narration (Seed Speech)",
                    ),
                )
                tracks, narr_assets = await self.narration.synthesize_plan(
                    job_id=job_id, plan=plan, language=job.language
                )
                await self._update(
                    job,
                    progress=JobProgress(
                        stage=PipelineStage.VIDEO,
                        percent=55,
                        message="Rendering scene videos (Seedance 2.0)",
                    ),
                )
                video_assets = await self.video_generation.generate_videos(job_id=job_id, plan=plan)
                await self._update(
                    job,
                    progress=JobProgress(
                        stage=PipelineStage.AVATAR,
                        percent=75,
                        message="Optional presenter clip (OmniHuman)",
                    ),
                )
                intro = plan.scenes[0].narration if plan.scenes else "Welcome."
                avatar_assets = await self.avatar.maybe_generate(
                    job_id=job_id,
                    presenter_image_path=job.presenter_image_path,
                    intro_script=intro[:500],
                )
                await self._update(
                    job,
                    progress=JobProgress(
                        stage=PipelineStage.VALIDATION,
                        percent=88,
                        message="Validating scenes against source (Seed 2.0)",
                    ),
                )
                issues = await self.validation.validate_plan(
                    source_text=job.source.normalized_text, plan=plan
                )
                await self._update(
                    job,
                    progress=JobProgress(
                        stage=PipelineStage.ASSEMBLY,
                        percent=95,
                        message="Assembling outputs",
                    ),
                )
                combined_assets = [*sb_assets, *narr_assets, *video_assets, *avatar_assets]
                any_demo = demo_mode or self.extraction.provider.health().demo_mode
                job.result = self.assembly.build_result(
                    job_id=job_id,
                    plan=plan,
                    storyboard_frames=frames,
                    narration_tracks=tracks,
                    media_assets=combined_assets,
                    validation_issues=issues,
                    demo_mode=any_demo,
                )
                await self.store.write_json_artifact(
                    job_id, "exports/final_program.json", job.result.model_dump(mode="json")
                )
                await self._update(
                    job,
                    status=JobStatus.COMPLETED,
                    progress=JobProgress(
                        stage=PipelineStage.ASSEMBLY,
                        percent=100,
                        message="Generation complete",
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("Generation pipeline failed for %s", job_id)
                job.status = JobStatus.FAILED
                job.error = str(exc)
                job.progress = JobProgress(
                    stage=PipelineStage.VIDEO, percent=100, message="Failed during generation"
                )
                await self.store.save(job)

    def spawn_review(self, job_id: str) -> None:
        task = asyncio.create_task(self.run_review_pipeline(job_id), name=f"review-{job_id}")
        self._tasks[job_id] = task

    def spawn_generate(self, job_id: str) -> None:
        task = asyncio.create_task(self.run_generation_pipeline(job_id), name=f"gen-{job_id}")
        self._tasks[job_id] = task
