from functools import lru_cache

from app.config import get_settings
from app.providers import (
    OmniHumanProvider,
    Seed2Provider,
    SeedanceProvider,
    SeedSpeechProvider,
    SeedreamProvider,
)
from app.services.assembly import AssemblyService
from app.services.avatar import AvatarService
from app.services.extraction import ExtractionService
from app.services.ingestion import IngestionService
from app.services.job_orchestrator import JobOrchestrator
from app.services.narration import NarrationService
from app.services.planning import PlanningService
from app.services.storyboard import StoryboardService
from app.services.validation import ValidationService
from app.services.video_generation import VideoGenerationService
from app.storage.job_store import JobStore


@lru_cache
def get_job_store() -> JobStore:
    return JobStore()


@lru_cache
def get_seed2() -> Seed2Provider:
    return Seed2Provider()


@lru_cache
def get_seedream() -> SeedreamProvider:
    return SeedreamProvider()


@lru_cache
def get_seedance() -> SeedanceProvider:
    return SeedanceProvider()


@lru_cache
def get_seed_speech() -> SeedSpeechProvider:
    return SeedSpeechProvider()


@lru_cache
def get_omnihuman() -> OmniHumanProvider:
    return OmniHumanProvider()


@lru_cache
def get_orchestrator() -> JobOrchestrator:
    store = get_job_store()
    seed2 = get_seed2()
    return JobOrchestrator(
        store=store,
        ingestion=IngestionService(store),
        extraction=ExtractionService(seed2),
        planning=PlanningService(seed2),
        storyboard=StoryboardService(get_seedream()),
        narration=NarrationService(get_seed_speech()),
        video_generation=VideoGenerationService(get_seedance()),
        avatar=AvatarService(get_omnihuman()),
        validation=ValidationService(seed2),
        assembly=AssemblyService(),
        settings=get_settings(),
    )
