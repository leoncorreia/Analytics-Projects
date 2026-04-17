import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

import aiofiles

from app.config import Settings, get_settings
from app.schemas.job import Job

logger = logging.getLogger(__name__)


class JobStore:
    """Local file-based persistence for jobs and uploads (swappable for cloud later)."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.root = Path(self.settings.data_dir).resolve()
        self.jobs_dir = self.root / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def new_job_id(self) -> str:
        return uuid.uuid4().hex

    def job_dir(self, job_id: str) -> Path:
        return self.jobs_dir / job_id

    def job_file(self, job_id: str) -> Path:
        return self.job_dir(job_id) / "job.json"

    def uploads_dir(self, job_id: str) -> Path:
        p = self.job_dir(job_id) / "uploads"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def assets_dir(self, job_id: str) -> Path:
        p = self.job_dir(job_id) / "assets"
        p.mkdir(parents=True, exist_ok=True)
        return p

    async def init_job(self, job: Job) -> None:
        self.job_dir(job.job_id).mkdir(parents=True, exist_ok=True)
        await self.save(job)

    async def save(self, job: Job) -> None:
        job.updated_at = datetime.now(timezone.utc)
        path = self.job_file(job.job_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        payload = job.model_dump(mode="json")
        async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
            await f.write(json.dumps(payload, indent=2))
        tmp.replace(path)
        logger.debug("Saved job %s", job.job_id)

    async def load(self, job_id: str) -> Job | None:
        path = self.job_file(job_id)
        if not path.exists():
            return None
        async with aiofiles.open(path, encoding="utf-8") as f:
            raw = await f.read()
        return Job.model_validate_json(raw)

    async def write_json_artifact(self, job_id: str, relative: str, payload: object) -> None:
        """Write JSON under jobs/{job_id}/{relative}."""
        path = self.job_dir(job_id) / relative.replace("\\", "/")
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        text = json.dumps(payload, indent=2)
        async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
            await f.write(text)
        tmp.replace(path)

    def relative_to_root(self, absolute: Path) -> str:
        try:
            return str(absolute.relative_to(self.root)).replace("\\", "/")
        except ValueError:
            return str(absolute).replace("\\", "/")
