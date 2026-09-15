from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Iterable

from .models import BloggerLinkJob
from .paths import jobs_path


class JobStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or jobs_path()

    def load_all(self) -> list[BloggerLinkJob]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("jobs.json root must be a list")
        return [BloggerLinkJob.from_dict(item) for item in raw]

    def save_all(self, jobs: Iterable[BloggerLinkJob]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps([j.to_dict() for j in jobs], ensure_ascii=False, indent=2)
        fd, temp_name = tempfile.mkstemp(prefix="jobs-", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(payload)
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def get(self, job_id: str) -> BloggerLinkJob:
        for job in self.load_all():
            if job.id == job_id:
                return job
        raise KeyError(job_id)

    def upsert(self, job: BloggerLinkJob) -> None:
        jobs = self.load_all()
        for i, existing in enumerate(jobs):
            if existing.id == job.id:
                jobs[i] = job
                break
        else:
            jobs.append(job)
        self.save_all(jobs)

    def delete(self, job_id: str) -> None:
        self.save_all([j for j in self.load_all() if j.id != job_id])
