from pydantic import BaseModel, Field


class StoryboardFrame(BaseModel):
    frame_id: str
    scene_id: str
    image_asset_id: str
    prompt_used: str
    order: int = 0


class NarrationTrack(BaseModel):
    track_id: str
    scene_id: str | None = None
    text: str
    audio_asset_id: str
    voice_profile: str | None = None
    language: str = "en"
