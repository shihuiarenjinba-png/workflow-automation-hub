from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .models import BloggerLinkJob, ScheduleSpec


class SchedulerError(RuntimeError):
    pass


@dataclass
class SchedulerCheck:
    ok: bool
    detail: str


WEEKDAYS = {"MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"}


def _safe_job_id(job_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]", "_", job_id)[:64]
    if not cleaned:
        raise SchedulerError("Invalid job id / ジョブIDが不正です")
    return cleaned


def task_name(job_id: str) -> str:
    return f"WorkflowAutomationHub_{_safe_job_id(job_id)}"


def validate_time(value: str) -> str:
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
        raise SchedulerError("Time must use HH:MM (24-hour) format / 時刻は24時間制のHH:MM形式で指定してください")
    return value


def runner_command(job_id: str) -> str:
    safe_id = _safe_job_id(job_id)
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable).resolve()
        return f'"{exe}" --run-job "{safe_id}"'
    exe = Path(sys.executable).resolve()
    entry = (Path(__file__).resolve().parent.parent / "desktop_app.py").resolve()
    return f'"{exe}" "{entry}" --run-job "{safe_id}"'


def build_create_args(job: BloggerLinkJob) -> list[str]:
    schedule: ScheduleSpec = job.schedule
    # /IT: run only while the current user is logged on. This avoids storing a
    # Windows account password and keeps the first release in an interactive-user
    # security context. /RL LIMITED prevents requesting elevated run level.
    args = [
        "schtasks", "/Create",
        "/TN", task_name(job.id),
        "/TR", runner_command(job.id),
        "/F",
        "/RL", "LIMITED",
        "/IT",
    ]
    if schedule.kind == "daily":
        args.extend(["/SC", "DAILY", "/ST", validate_time(schedule.time)])
    elif schedule.kind == "weekly":
        days = [day for day in schedule.weekdays if day in WEEKDAYS]
        if not days:
            raise SchedulerError("At least one weekday is required / 曜日を1つ以上選択してください")
        args.extend(["/SC", "WEEKLY", "/D", ",".join(days), "/ST", validate_time(schedule.time)])
    elif schedule.kind == "logon":
        args.extend(["/SC", "ONLOGON"])
    else:
        raise SchedulerError(f"Unsupported schedule kind / 未対応のスケジュール種別: {schedule.kind}")
    return args


class WindowsTaskScheduler:
    def check(self) -> SchedulerCheck:
        if os.name != "nt":
            return SchedulerCheck(False, "Windows Task Scheduler is available only on Windows / Windowsでのみ利用できます")
        if not shutil.which("schtasks"):
            return SchedulerCheck(False, "schtasks.exe was not found / schtasks.exeが見つかりません")
        result = subprocess.run(
            ["schtasks", "/Query", "/FO", "LIST"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            shell=False,
        )
        return SchedulerCheck(result.returncode == 0, (result.stdout or result.stderr).strip()[:500])

    def register(self, job: BloggerLinkJob) -> None:
        if os.name != "nt":
            raise SchedulerError("Windows Task Scheduler is available only on Windows / Windowsでのみ利用できます")
        result = subprocess.run(
            build_create_args(job),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            shell=False,
        )
        if result.returncode != 0:
            raise SchedulerError((result.stderr or result.stdout).strip())

    def unregister(self, job_id: str) -> None:
        if os.name != "nt":
            raise SchedulerError("Windows Task Scheduler is available only on Windows / Windowsでのみ利用できます")
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", task_name(job_id), "/F"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            shell=False,
        )
        if result.returncode != 0:
            message = (result.stderr or result.stdout).strip()
            if "cannot find" not in message.lower() and "見つかりません" not in message:
                raise SchedulerError(message)
