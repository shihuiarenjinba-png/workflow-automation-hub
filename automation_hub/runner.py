from __future__ import annotations

from .audit import AuditLogger
from .blogger_automation import JobRunResult, run_link_job
from .google_blogger import GoogleBloggerConnector
from .jobs import JobStore
from .models import validate_job_id


def run_saved_job(job_id: str, *, dry_run: bool = False) -> JobRunResult:
    job_id = validate_job_id(job_id)
    job = JobStore().get(job_id)
    if not job.enabled:
        raise RuntimeError(f"Job is disabled / ジョブは無効です: {job_id}")
    connector = GoogleBloggerConnector()
    return run_link_job(connector, job, dry_run=dry_run, audit=AuditLogger())
