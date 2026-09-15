from __future__ import annotations

from pathlib import Path

from .audit import AuditLogger
from .blogger_automation import JobRunResult, run_link_job
from .google_blogger import GoogleBloggerConnector
from .jobs import JobStore
from .settings import SettingsStore
from .storage import DPAPITokenVault


def run_saved_job(job_id: str, *, dry_run: bool = False) -> JobRunResult:
    settings = SettingsStore().load()
    credentials_file = str(settings.get("google_credentials_file", "")).strip()
    if not credentials_file:
        raise RuntimeError("Google OAuth credentials file is not configured")
    job = JobStore().get(job_id)
    if not job.enabled:
        raise RuntimeError(f"Job is disabled: {job_id}")
    connector = GoogleBloggerConnector(Path(credentials_file), DPAPITokenVault())
    return run_link_job(connector, job, dry_run=dry_run, audit=AuditLogger())
