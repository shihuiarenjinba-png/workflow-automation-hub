"""Capture reproducible, credential-free Windows GUI screenshots for review.

Requires Windows PowerShell with System.Drawing and an interactive desktop.
Only artificial job data and stubbed Google/scheduler clients are used.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from automation_hub import gui as gui_module  # noqa: E402
from automation_hub.jobs import JobStore  # noqa: E402
from automation_hub.models import BloggerLinkJob  # noqa: E402
from automation_hub.schedule_approval import ScheduleApprovalStore  # noqa: E402
from automation_hub.settings import SettingsStore  # noqa: E402


def capture(root, path: Path) -> dict:
    root.update_idletasks()
    root.update()
    left, top = int(root.winfo_rootx()), int(root.winfo_rooty())
    width, height = int(root.winfo_width()), int(root.winfo_height())
    if width < 400 or height < 300 or left < 0 or top < 0:
        raise RuntimeError("No usable desktop window for screenshot")
    path.parent.mkdir(parents=True, exist_ok=True)
    # The captured window is an isolated mock-only fixture. Never capture real
    # desktop credentials, tokens, browser pages or other external windows.
    ps = r"""
param([int]$X,[int]$Y,[int]$Width,[int]$Height,[string]$Output)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$bmp = [System.Drawing.Bitmap]::new($Width,$Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
try {
  $g.CopyFromScreen($X,$Y,0,0,$bmp.Size)
  $bmp.Save($Output,[System.Drawing.Imaging.ImageFormat]::Png)
} finally {
  $g.Dispose()
  $bmp.Dispose()
}
"""
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "capture.ps1"
        script.write_text(ps, encoding="utf-8-sig")
        command = [
            "powershell.exe", "-NoProfile", "-NonInteractive",
            "-ExecutionPolicy", "Bypass", "-File", str(script),
            "-X", str(left), "-Y", str(top), "-Width", str(width),
            "-Height", str(height), "-Output", str(path.resolve()),
        ]
        p = subprocess.run(command, check=False, capture_output=True,
                           text=True, timeout=30)
        if p.returncode != 0 or not path.is_file() or path.stat().st_size < 1000:
            raise RuntimeError(
                f"Windows screenshot failed (code {p.returncode}): "
                f"{(p.stderr or p.stdout)[-250:]}"
            )
    return {"file": path.name, "width": width, "height": height,
            "bytes": path.stat().st_size, "x": left, "y": top}


def main() -> int:
    if sys.platform != "win32":
        raise RuntimeError("GUI screenshot capture requires Windows")
    import tkinter as tk

    output = ROOT / "gui-review-evidence"
    output.mkdir(exist_ok=True)
    report = {"source": "GitHub-hosted Windows test fixture",
              "auth_mode": "fully mocked; no user data",
              "cases": [], "failures": []}
    with tempfile.TemporaryDirectory() as tmp:
        data_root = Path(tmp)
        jobs = JobStore(data_root / "jobs.json")
        settings = SettingsStore(data_root / "settings.json")
        approvals = ScheduleApprovalStore(data_root / "approvals.json")
        sample = BloggerLinkJob(
            id="sample-demo",
            name="Sample Blogger link",
            blog_id="sample-blog",
            target_text="Learn about our products",
            anchor_text="View products",
            link_url="https://example.com/products",
            max_posts=5,
        )
        jobs.upsert(sample)
        google = MagicMock()
        google.has_client_config.return_value = False
        google.has_token.return_value = False
        scheduler = MagicMock()
        root = tk.Tk()
        root.withdraw()
        with patch.object(gui_module, "SettingsStore", return_value=settings), \
             patch.object(gui_module, "JobStore", return_value=jobs), \
             patch.object(gui_module, "ScheduleApprovalStore", return_value=approvals), \
             patch.object(gui_module, "GoogleBloggerConnector", return_value=google), \
             patch.object(gui_module, "WindowsTaskScheduler", return_value=scheduler):
            app = gui_module.AutomationHubGUI(root)
        try:
            screen_width = int(root.winfo_screenwidth())
            screen_height = int(root.winfo_screenheight())
            width, height = min(1020, screen_width - 60), min(760, screen_height - 90)
            if width < 840 or height < 580:
                raise RuntimeError(f"Desktop too small for supported GUI: {screen_width}x{screen_height}")
            root.geometry(f"{width}x{height}+20+20")
            root.deiconify()
            root.lift()
            root.update()
            app.selected_job_id = sample.id
            app.load_job(sample.id)
            layouts = [
                ("ja-home", 0, "ja", 1.0),
                ("ja-connect", 1, "ja", 1.0),
                ("ja-jobs", 2, "ja", 1.0),
                ("ja-schedule", 3, "ja", 1.0),
                ("ja-jobs-150", 2, "ja", 1.5),
                ("ja-jobs-150-bottom", 2, "ja", 1.5),
                ("en-home", 0, "en", 1.0),
            ]
            baseline_scaling = float(root.tk.call("tk", "scaling"))
            last_scaling = None
            for name, tab, lang, scaling in layouts:
                try:
                    # A 100% comparison means the runner's native DPI scale,
                    # not Tk's absolute 1.0 (~72 DPI). Simulate 150% relative
                    # to that baseline, then rebuild all widgets.
                    actual_scaling = baseline_scaling * scaling
                    if actual_scaling != last_scaling:
                        root.tk.call("tk", "scaling", actual_scaling)
                        app.build_ui()
                        app.selected_job_id = sample.id
                        app.load_job(sample.id)
                        last_scaling = actual_scaling
                    target_locale = "English" if lang == "en" else "日本語"
                    if app.language_var.get() != target_locale:
                        app.language_var.set(target_locale)
                        app.on_language_change()
                    app.notebook.select(tab)
                    root.update_idletasks()
                    root.update()
                    frame = [app.home_tab, app.google_tab, app.jobs_tab,
                             app.schedule_tab, app.compliance_tab][tab]
                    if tab == 2:
                        # Check the actual inner editor width, not just the
                        # new scrollable Canvas wrapper width.
                        frame = app.job_inner
                        visible_width = app.job_canvas.winfo_width()
                        if name.endswith("-bottom"):
                            app.job_canvas.yview_moveto(1.0)
                        else:
                            app.job_canvas.yview_moveto(0.0)
                        root.update_idletasks()
                        root.update()
                    else:
                        visible_width = frame.winfo_width()
                    data = capture(root, output / f"{name}.png")
                    data.update({"tab": tab, "locale": lang, "relative_scaling": scaling,
                                 "tk_scaling": actual_scaling,
                                 "requested_width": frame.winfo_reqwidth(),
                                 "visible_width": visible_width,
                                 "clipped_horizontally": frame.winfo_reqwidth() > visible_width + 8})
                    report["cases"].append(data)
                except Exception as exc:
                    report["failures"].append({"case": name, "error": type(exc).__name__,
                                               "detail": str(exc)[:300]})
        finally:
            root.destroy()
    (output / "review_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({"captures": len(report["cases"]),
                      "failures": report["failures"],
                      "possibly_clipped": [x["file"] for x in report["cases"] if x["clipped_horizontally"]]},
                     ensure_ascii=False))
    return 0 if len(report["cases"]) == 7 and not report["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
