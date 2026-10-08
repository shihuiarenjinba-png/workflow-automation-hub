from __future__ import annotations

import json
import os
import time
from pathlib import Path

from .models import validate_job_id
from .paths import job_lock_dir


class JobAlreadyRunningError(RuntimeError):
    pass


class JobExecutionLock:
    def __init__(self, job_id: str, *, root: Path | None = None, stale_seconds: int = 6 * 60 * 60) -> None:
        self.job_id = validate_job_id(job_id)
        self.root = root or job_lock_dir()
        self.stale_seconds = max(int(stale_seconds), 60)
        self.path = self.root / f"{self.job_id}.lock"
        self.acquired = False

    def _remove_if_stale(self) -> None:
        try:
            age = time.time() - self.path.stat().st_mtime
        except FileNotFoundError:
            return
        if age > self.stale_seconds:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass

    def acquire(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self._remove_if_stale()
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            fd = os.open(self.path, flags, 0o600)
        except FileExistsError as exc:
            raise JobAlreadyRunningError(
                f"Job is already running: {self.job_id} / ジョブはすでに実行中です: {self.job_id}"
            ) from exc
        try:
            payload = json.dumps({"pid": os.getpid(), "created_at": time.time(), "job_id": self.job_id})
            os.write(fd, payload.encode("utf-8"))
            os.fsync(fd)
            self.acquired = True
        finally:
            os.close(fd)

    def release(self) -> None:
        if not self.acquired:
            return
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
        finally:
            self.acquired = False

    def __enter__(self) -> "JobExecutionLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()
