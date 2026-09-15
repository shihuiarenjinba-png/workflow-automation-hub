from __future__ import annotations

import queue
import threading
import uuid
from pathlib import Path
from tkinter import BooleanVar, Listbox, StringVar, Tk, filedialog, messagebox
from tkinter import ttk
from typing import Any, Callable, TypeVar

from .blogger_automation import run_link_job
from .google_blogger import GoogleBloggerConnector
from .i18n import SUPPORTED_LOCALES, tr
from .jobs import JobStore, JobStoreError
from .models import BloggerLinkJob, ScheduleSpec
from .scheduler import WindowsTaskScheduler
from .settings import SettingsStore

T = TypeVar("T")


class AutomationHubGUI:
    def __init__(self, root: Tk) -> None:
        self.root = root
        self.settings_store = SettingsStore()
        self.job_store = JobStore()
        self.scheduler = WindowsTaskScheduler()
        self.google = GoogleBloggerConnector()
        self.settings = self.settings_store.load()
        self.locale = str(self.settings.get("locale", "ja"))
        if self.locale not in SUPPORTED_LOCALES:
            self.locale = "ja"
        self.blogs: list[dict[str, str]] = []
        self.blog_display_to_id: dict[str, str] = {}
        self.selected_job_id: str | None = None
        self.busy = False
        self._async_queue: queue.Queue[tuple[str, Any, Callable[[Any], None] | None]] = queue.Queue()
        self.root.geometry("940x670")
        self.root.minsize(840, 580)
        self._migrate_legacy_google_config()
        self.build_ui()
        self.root.after(100, self._poll_async_queue)

    def t(self, key: str, **kwargs: object) -> str:
        return tr(self.locale, key, **kwargs)

    def _migrate_legacy_google_config(self) -> None:
        legacy = str(self.settings.pop("_legacy_google_credentials_file", "") or "").strip()
        if not legacy or self.google.has_client_config():
            return
        try:
            source = Path(legacy)
            if source.is_file():
                result = self.google.import_client_config(source)
                self.settings["google_client_id_hint"] = result.metadata.client_id_hint
                self.settings["google_project_id"] = result.metadata.project_id
                self.settings_store.save(self.settings)
        except Exception:
            # Legacy migration must never prevent the GUI from starting.
            pass

    def build_ui(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()
        self.root.title(self.t("app_title"))
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text=self.t("language")).pack(side="left")
        self.language_var = StringVar(value="日本語" if self.locale == "ja" else "English")
        lang = ttk.Combobox(top, textvariable=self.language_var, values=["日本語", "English"], state="readonly", width=10)
        lang.pack(side="left", padx=(6, 12))
        lang.bind("<<ComboboxSelected>>", self.on_language_change)
        ttk.Label(top, text=self.t("desktop_note")).pack(side="left", padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.google_tab = ttk.Frame(self.notebook, padding=14)
        self.jobs_tab = ttk.Frame(self.notebook, padding=14)
        self.schedule_tab = ttk.Frame(self.notebook, padding=14)
        self.compliance_tab = ttk.Frame(self.notebook, padding=14)
        self.notebook.add(self.google_tab, text=self.t("tab_google"))
        self.notebook.add(self.jobs_tab, text=self.t("tab_jobs"))
        self.notebook.add(self.schedule_tab, text=self.t("tab_schedule"))
        self.notebook.add(self.compliance_tab, text=self.t("tab_compliance"))
        self._build_google_tab()
        self._build_jobs_tab()
        self._build_schedule_tab()
        self._build_compliance_tab()
        self.refresh_jobs(show_error=False)

    def _google_status_text(self) -> str:
        client = self.t("oauth_imported") if self.google.has_client_config() else self.t("oauth_not_imported")
        token = self.t("status_connected") if self.google.has_token() else self.t("status_not_connected")
        return f"{self.t('oauth_config_status')}: {client}    {self.t('google_auth_status')}: {token}"

    def _client_info_text(self) -> str:
        if not self.google.has_client_config():
            return ""
        try:
            metadata = self.google.client_metadata()
            project = metadata.project_id or "-"
            return self.t("oauth_client_info", client_id=metadata.client_id_hint, project_id=project)
        except Exception as exc:
            return f"{self.t('oauth_config_invalid')}: {exc}"

    def _build_google_tab(self) -> None:
        frame = self.google_tab
        ttk.Label(frame, text=self.t("google_help"), wraplength=850, justify="left").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )
        buttons = ttk.Frame(frame)
        buttons.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))
        ttk.Button(buttons, text=self.t("import_oauth"), command=self.choose_credentials).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text=self.t("authenticate"), command=self.authenticate_google).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text=self.t("connection_test"), command=self.test_google).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text=self.t("load_blogs"), command=self.load_blogs).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text=self.t("disconnect"), command=self.disconnect_google).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text=self.t("remove_oauth_config"), command=self.remove_google_config).pack(side="left")

        self.google_status_var = StringVar(value=self._google_status_text())
        ttk.Label(frame, textvariable=self.google_status_var, wraplength=850).grid(row=2, column=0, columnspan=2, sticky="w")
        self.client_info_var = StringVar(value=self._client_info_text())
        ttk.Label(frame, textvariable=self.client_info_var, wraplength=850).grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.blog_text_var = StringVar(value="")
        ttk.Label(frame, textvariable=self.blog_text_var, wraplength=850).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))

    def _build_jobs_tab(self) -> None:
        outer = self.jobs_tab
        left = ttk.Frame(outer)
        left.pack(side="left", fill="y", padx=(0, 18))
        right = ttk.Frame(outer)
        right.pack(side="left", fill="both", expand=True)
        ttk.Label(left, text=self.t("jobs")).pack(anchor="w")
        self.jobs_list = Listbox(left, width=30, height=24, exportselection=False)
        self.jobs_list.pack(fill="y", expand=True, pady=6)
        self.jobs_list.bind("<<ListboxSelect>>", self.on_job_select)
        ttk.Button(left, text=self.t("new_job"), command=self.new_job).pack(fill="x", pady=(4, 0))

        self.job_name_var = StringVar()
        self.blog_var = StringVar()
        self.target_var = StringVar()
        self.anchor_var = StringVar()
        self.link_var = StringVar()
        self.max_posts_var = StringVar(value="50")
        self.enabled_var = BooleanVar(value=True)
        fields = [
            ("job_name", self.job_name_var), ("blog", self.blog_var), ("target_text", self.target_var),
            ("anchor_text", self.anchor_var), ("link_url", self.link_var), ("max_posts", self.max_posts_var),
        ]
        for row, (key, variable) in enumerate(fields):
            ttk.Label(right, text=self.t(key)).grid(row=row, column=0, sticky="w", pady=5)
            if key == "blog":
                self.blog_combo = ttk.Combobox(right, textvariable=variable, state="normal", width=60)
                self.blog_combo.grid(row=row, column=1, sticky="ew", padx=8)
            else:
                ttk.Entry(right, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=8)
        right.columnconfigure(1, weight=1)
        ttk.Checkbutton(right, text=self.t("enabled"), variable=self.enabled_var).grid(row=6, column=1, sticky="w", padx=8, pady=5)
        actions = ttk.Frame(right)
        actions.grid(row=7, column=0, columnspan=2, sticky="w", pady=18)
        ttk.Button(actions, text=self.t("save_job"), command=self.save_job).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text=self.t("run_dry"), command=lambda: self.run_job(True)).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text=self.t("run_now"), command=lambda: self.run_job(False)).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text=self.t("delete_job"), command=self.delete_job).pack(side="left")

    def _build_schedule_tab(self) -> None:
        frame = self.schedule_tab
        self.schedule_job_var = StringVar()
        self.schedule_kind_var = StringVar(value=self.t("daily"))
        self.schedule_time_var = StringVar(value="08:00")
        self.weekday_vars = {
            day: BooleanVar(value=day in {"MON", "TUE", "WED", "THU", "FRI"})
            for day in ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        }
        ttk.Label(frame, text=self.t("jobs")).grid(row=0, column=0, sticky="w", pady=6)
        self.schedule_job_combo = ttk.Combobox(frame, textvariable=self.schedule_job_var, state="readonly", width=52)
        self.schedule_job_combo.grid(row=0, column=1, sticky="w", padx=8)
        self.schedule_job_combo.bind("<<ComboboxSelected>>", self.on_schedule_job_select)
        ttk.Label(frame, text=self.t("schedule_kind")).grid(row=1, column=0, sticky="w", pady=6)
        self.schedule_kind_combo = ttk.Combobox(
            frame, textvariable=self.schedule_kind_var, state="readonly",
            values=[self.t("daily"), self.t("weekly"), self.t("logon")], width=25,
        )
        self.schedule_kind_combo.grid(row=1, column=1, sticky="w", padx=8)
        ttk.Label(frame, text=self.t("time")).grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.schedule_time_var, width=10).grid(row=2, column=1, sticky="w", padx=8)
        ttk.Label(frame, text=self.t("weekdays")).grid(row=3, column=0, sticky="nw", pady=6)
        weekdays_frame = ttk.Frame(frame)
        weekdays_frame.grid(row=3, column=1, sticky="w", padx=8)
        names = [
            ("MON", "monday"), ("TUE", "tuesday"), ("WED", "wednesday"), ("THU", "thursday"),
            ("FRI", "friday"), ("SAT", "saturday"), ("SUN", "sunday"),
        ]
        for index, (day, key) in enumerate(names):
            ttk.Checkbutton(weekdays_frame, text=self.t(key), variable=self.weekday_vars[day]).grid(row=0, column=index, padx=(0, 6))
        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, columnspan=2, sticky="w", pady=20)
        ttk.Button(buttons, text=self.t("save"), command=self.save_schedule_to_job).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text=self.t("register_schedule"), command=self.register_schedule).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text=self.t("remove_schedule"), command=self.remove_schedule).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text=self.t("test_scheduler"), command=self.test_scheduler).pack(side="left")
        self.scheduler_status_var = StringVar(value="")
        ttk.Label(frame, textvariable=self.scheduler_status_var, wraplength=800).grid(row=5, column=0, columnspan=2, sticky="w")

    def _build_compliance_tab(self) -> None:
        text = "\n\n".join([
            self.t("supported_api_note"), self.t("free_setup"), self.t("review_date"), self.t("blogger_compliance"),
            self.t("scheduler_compliance"), self.t("compliance_note"),
        ])
        ttk.Label(self.compliance_tab, text=text, wraplength=850, justify="left").pack(anchor="w")

    def on_language_change(self, _event: object = None) -> None:
        self.locale = "ja" if self.language_var.get() == "日本語" else "en"
        self.settings["locale"] = self.locale
        self.settings_store.save(self.settings)
        self.build_ui()

    def choose_credentials(self) -> None:
        path = filedialog.askopenfilename(
            title=self.t("select_credentials"),
            filetypes=[("Google OAuth JSON", "*.json"), ("JSON", "*.json")],
        )
        if not path:
            return
        try:
            result = self.google.import_client_config(Path(path))
            self.settings["google_client_id_hint"] = result.metadata.client_id_hint
            self.settings["google_project_id"] = result.metadata.project_id
            self.settings_store.save(self.settings)
            self.google_status_var.set(self._google_status_text())
            self.client_info_var.set(self._client_info_text())
            key = "oauth_imported_token_reset" if result.token_reset else "oauth_imported_ok"
            messagebox.showinfo(self.t("info_title"), self.t(key))
        except Exception as exc:
            messagebox.showerror(self.t("error_title"), str(exc))

    def _set_busy(self, value: bool) -> None:
        self.busy = value
        self.root.config(cursor="watch" if value else "")

    def run_async(self, func: Callable[[], T], on_success: Callable[[T], None]) -> None:
        if self.busy:
            return
        self._set_busy(True)

        def worker() -> None:
            try:
                value = func()
            except Exception as exc:
                self._async_queue.put(("error", exc, None))
            else:
                self._async_queue.put(("ok", value, on_success))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_async_queue(self) -> None:
        try:
            while True:
                kind, value, callback = self._async_queue.get_nowait()
                self._set_busy(False)
                if kind == "error":
                    messagebox.showerror(self.t("error_title"), str(value))
                elif callback is not None:
                    try:
                        callback(value)
                    except Exception as exc:
                        messagebox.showerror(self.t("error_title"), str(exc))
        except queue.Empty:
            pass
        self.root.after(100, self._poll_async_queue)

    def authenticate_google(self) -> None:
        self.run_async(lambda: self.google.authenticate(self.locale), lambda _value: self._after_auth())

    def _after_auth(self) -> None:
        self.google_status_var.set(self._google_status_text())
        messagebox.showinfo(self.t("info_title"), self.t("auth_completed"))
        self.load_blogs()

    def test_google(self) -> None:
        self.run_async(self.google.check_connection, lambda result: self._after_google_test(result.blogs))

    def _after_google_test(self, blogs: list[dict[str, str]]) -> None:
        self._set_blogs(blogs)
        self.google_status_var.set(self._google_status_text())
        messagebox.showinfo(self.t("info_title"), self.t("google_connected"))

    def load_blogs(self) -> None:
        self.run_async(self.google.list_blogs, self._after_blogs_loaded)

    def _after_blogs_loaded(self, blogs: list[dict[str, str]]) -> None:
        self._set_blogs(blogs)
        self.blog_text_var.set(self.t("blogs_loaded", count=len(blogs)))

    def _set_blogs(self, blogs: list[dict[str, str]]) -> None:
        self.blogs = blogs
        self.blog_display_to_id = {}
        displays: list[str] = []
        for blog in blogs:
            display = f"{blog.get('name', '')} — {blog.get('url', '')}".strip(" —") or blog.get("id", "")
            displays.append(display)
            self.blog_display_to_id[display] = blog.get("id", "")
        if hasattr(self, "blog_combo"):
            self.blog_combo["values"] = displays

    def disconnect_google(self) -> None:
        if not messagebox.askyesno(self.t("warning_title"), self.t("confirm_disconnect")):
            return
        try:
            self.google.disconnect()
            self.google_status_var.set(self._google_status_text())
            messagebox.showinfo(self.t("info_title"), self.t("google_disconnected"))
        except Exception as exc:
            messagebox.showerror(self.t("error_title"), str(exc))

    def remove_google_config(self) -> None:
        if not messagebox.askyesno(self.t("warning_title"), self.t("confirm_remove_oauth")):
            return
        try:
            self.google.remove_client_config()
            self.settings["google_client_id_hint"] = ""
            self.settings["google_project_id"] = ""
            self.settings_store.save(self.settings)
            self.google_status_var.set(self._google_status_text())
            self.client_info_var.set("")
            self.blogs = []
            self.blog_display_to_id = {}
            if hasattr(self, "blog_combo"):
                self.blog_combo["values"] = []
            messagebox.showinfo(self.t("info_title"), self.t("oauth_removed"))
        except Exception as exc:
            messagebox.showerror(self.t("error_title"), str(exc))

    def refresh_jobs(self, *, show_error: bool = True) -> None:
        try:
            jobs = self.job_store.load_all()
        except JobStoreError as exc:
            if hasattr(self, "jobs_list"):
                self.jobs_list.delete(0, "end")
            if hasattr(self, "schedule_job_combo"):
                self.schedule_job_combo["values"] = []
            if show_error:
                messagebox.showerror(self.t("error_title"), str(exc))
            return
        if hasattr(self, "jobs_list"):
            self.jobs_list.delete(0, "end")
            for job in jobs:
                self.jobs_list.insert("end", f"{job.name} [{job.id}]")
        if hasattr(self, "schedule_job_combo"):
            self.schedule_job_combo["values"] = [f"{job.name} [{job.id}]" for job in jobs]

    def new_job(self) -> None:
        self.selected_job_id = None
        self.job_name_var.set("")
        self.blog_var.set("")
        self.target_var.set("")
        self.anchor_var.set("")
        self.link_var.set("")
        self.max_posts_var.set("50")
        self.enabled_var.set(True)
        self.jobs_list.selection_clear(0, "end")

    @staticmethod
    def _id_from_display(display: str) -> str:
        if display.endswith("]") and "[" in display:
            return display.rsplit("[", 1)[1][:-1]
        return display

    def on_job_select(self, _event: object = None) -> None:
        selection = self.jobs_list.curselection()
        if not selection:
            return
        self.selected_job_id = self._id_from_display(self.jobs_list.get(selection[0]))
        try:
            self.load_job(self.selected_job_id)
        except Exception as exc:
            messagebox.showerror(self.t("error_title"), str(exc))

    def load_job(self, job_id: str) -> None:
        job = self.job_store.get(job_id)
        self.job_name_var.set(job.name)
        self.blog_var.set(next((display for display, bid in self.blog_display_to_id.items() if bid == job.blog_id), job.blog_id))
        self.target_var.set(job.target_text)
        self.anchor_var.set(job.anchor_text)
        self.link_var.set(job.link_url)
        self.max_posts_var.set(str(job.max_posts))
        self.enabled_var.set(job.enabled)
        self._load_schedule_fields(job)

    def _form_job(self) -> BloggerLinkJob:
        blog_display = self.blog_var.get().strip()
        blog_id = self.blog_display_to_id.get(blog_display, blog_display)
        job_id = self.selected_job_id or uuid.uuid4().hex[:12]
        try:
            schedule = self.job_store.get(job_id).schedule
        except KeyError:
            schedule = ScheduleSpec()
        return BloggerLinkJob(
            id=job_id,
            name=self.job_name_var.get(),
            blog_id=blog_id,
            target_text=self.target_var.get(),
            link_url=self.link_var.get(),
            anchor_text=self.anchor_var.get() or self.target_var.get(),
            max_posts=int(self.max_posts_var.get()),
            enabled=self.enabled_var.get(),
            schedule=schedule,
        )

    def save_job(self) -> None:
        try:
            job = self._form_job()
            self.job_store.upsert(job)
            self.selected_job_id = job.id
            self.refresh_jobs(show_error=False)
            messagebox.showinfo(self.t("info_title"), self.t("saved"))
        except Exception as exc:
            messagebox.showerror(self.t("error_title"), str(exc))

    def delete_job(self) -> None:
        if not self.selected_job_id:
            messagebox.showinfo(self.t("info_title"), self.t("select_job_first"))
            return
        if not messagebox.askyesno(self.t("warning_title"), self.t("confirm_delete")):
            return
        job_id = self.selected_job_id
        try:
            try:
                self.scheduler.unregister(job_id)
            except Exception:
                pass
            self.job_store.delete(job_id)
            self.selected_job_id = None
            self.new_job()
            self.refresh_jobs(show_error=False)
            messagebox.showinfo(self.t("info_title"), self.t("deleted"))
        except Exception as exc:
            messagebox.showerror(self.t("error_title"), str(exc))

    def run_job(self, dry_run: bool) -> None:
        if not self.selected_job_id:
            messagebox.showinfo(self.t("info_title"), self.t("select_job_first"))
            return
        if not dry_run and not messagebox.askyesno(self.t("warning_title"), self.t("confirm_run")):
            return
        try:
            job = self.job_store.get(self.selected_job_id)
        except Exception as exc:
            messagebox.showerror(self.t("error_title"), str(exc))
            return
        self.run_async(
            lambda: run_link_job(self.google, job, dry_run=dry_run),
            lambda result: messagebox.showinfo(
                self.t("info_title"),
                self.t("dry_result" if dry_run else "run_result", scanned=result.scanned, changed=result.changed),
            ),
        )

    def on_schedule_job_select(self, _event: object = None) -> None:
        display = self.schedule_job_var.get()
        if display:
            try:
                self.selected_job_id = self._id_from_display(display)
                self._load_schedule_fields(self.job_store.get(self.selected_job_id))
            except Exception as exc:
                messagebox.showerror(self.t("error_title"), str(exc))

    def _load_schedule_fields(self, job: BloggerLinkJob) -> None:
        if not hasattr(self, "schedule_kind_var"):
            return
        labels = {"daily": self.t("daily"), "weekly": self.t("weekly"), "logon": self.t("logon")}
        self.schedule_kind_var.set(labels.get(job.schedule.kind, self.t("daily")))
        self.schedule_time_var.set(job.schedule.time)
        for day, var in self.weekday_vars.items():
            var.set(day in job.schedule.weekdays)
        self.schedule_job_var.set(f"{job.name} [{job.id}]")

    def _schedule_from_fields(self) -> ScheduleSpec:
        reverse = {self.t("daily"): "daily", self.t("weekly"): "weekly", self.t("logon"): "logon"}
        return ScheduleSpec(
            kind=reverse.get(self.schedule_kind_var.get(), "daily"),
            time=self.schedule_time_var.get().strip(),
            weekdays=[day for day, var in self.weekday_vars.items() if var.get()],
        )

    def save_schedule_to_job(self) -> BloggerLinkJob | None:
        if not self.selected_job_id:
            display = self.schedule_job_var.get()
            if display:
                self.selected_job_id = self._id_from_display(display)
        if not self.selected_job_id:
            messagebox.showinfo(self.t("info_title"), self.t("select_job_first"))
            return None
        try:
            job = self.job_store.get(self.selected_job_id)
            job.schedule = self._schedule_from_fields()
            self.job_store.upsert(job)
            self.refresh_jobs(show_error=False)
            messagebox.showinfo(self.t("info_title"), self.t("saved"))
            return job
        except Exception as exc:
            messagebox.showerror(self.t("error_title"), str(exc))
            return None

    def register_schedule(self) -> None:
        job = self.save_schedule_to_job()
        if job is None:
            return
        try:
            self.scheduler.register(job)
            messagebox.showinfo(self.t("info_title"), self.t("schedule_registered"))
        except Exception as exc:
            messagebox.showerror(self.t("error_title"), str(exc))

    def remove_schedule(self) -> None:
        if not self.selected_job_id:
            messagebox.showinfo(self.t("info_title"), self.t("select_job_first"))
            return
        try:
            self.scheduler.unregister(self.selected_job_id)
            messagebox.showinfo(self.t("info_title"), self.t("schedule_removed"))
        except Exception as exc:
            messagebox.showerror(self.t("error_title"), str(exc))

    def test_scheduler(self) -> None:
        check = self.scheduler.check()
        self.scheduler_status_var.set(
            self.t("status_scheduler_ok") if check.ok else f"{self.t('status_scheduler_ng')}: {check.detail}"
        )


def launch_gui() -> None:
    root = Tk()
    AutomationHubGUI(root)
    root.mainloop()
