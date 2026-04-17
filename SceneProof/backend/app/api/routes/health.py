from fastapi import APIRouter

from app.deps import get_omnihuman, get_seed2, get_seedance, get_seed_speech, get_seedream

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "providers": {
            "seed2": get_seed2().health().model_dump(),
            "seedream": get_seedream().health().model_dump(),
            "seedance": get_seedance().health().model_dump(),
            "seed_speech": get_seed_speech().health().model_dump(),
            "omnihuman": get_omnihuman().health().model_dump(),
        },
    }
