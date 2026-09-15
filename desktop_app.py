from __future__ import annotations

import argparse
import sys

from automation_hub.audit import AuditLogger
from automation_hub.i18n import tr
from automation_hub.settings import SettingsStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Workflow Automation Hub / ワークフロー自動化ハブ")
    parser.add_argument("--run-job", help="Run a saved Blogger job / 保存済みBloggerジョブを実行")
    parser.add_argument("--dry-run", action="store_true", help="Preview only / 変更せず確認のみ")
    args = parser.parse_args()
    locale = str(SettingsStore().load().get("locale", "ja"))
    if args.run_job:
        from automation_hub.runner import run_saved_job
        audit = AuditLogger()
        try:
            result = run_saved_job(args.run_job, dry_run=args.dry_run)
            message = tr(locale, "dry_result" if args.dry_run else "run_result", scanned=result.scanned, changed=result.changed)
            audit.write("scheduled_job_ok", job_id=args.run_job, dry_run=args.dry_run, scanned=result.scanned, changed=result.changed)
            print(message)
            return 0
        except Exception as exc:
            audit.write("scheduled_job_error", job_id=args.run_job, dry_run=args.dry_run, error=type(exc).__name__, detail=str(exc)[:1000])
            print(f"{tr(locale, 'status_error')}: {exc}", file=sys.stderr)
            return 1
    from automation_hub.gui import launch_gui
    launch_gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
