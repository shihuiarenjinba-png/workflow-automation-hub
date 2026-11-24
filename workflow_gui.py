from __future__ import annotations

import contextlib
import io
import json
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from workflow_hub import Runner


def load_workflow(path: str | Path) -> dict:
    return json.loads(Path(path).expanduser().resolve().read_text(encoding="utf-8"))


def execute_workflow(path: str | Path, *, dry_run: bool = True) -> str:
    config = load_workflow(path)
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        Runner(config, dry_run=dry_run).run()
    return stream.getvalue()


class WorkflowGui(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Workflow Automation Hub")
        self.geometry("780x520")
        self.minsize(620, 400)
        self.path_var = tk.StringVar()
        self.dry_run_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="設定JSONを選択してください。Dry Runが初期状態です。")
        self.events: queue.Queue = queue.Queue()
        self.worker: threading.Thread | None = None
        self._build()
        self.after(100, self._poll)

    def _build(self) -> None:
        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)
        root.columnconfigure(1, weight=1)
        ttk.Label(root, text="Workflow Automation Hub", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(root, text="設定を選択し、まずDry Runで内容を確認してから実行します。", wraplength=700).grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 12))
        ttk.Label(root, text="設定JSON").grid(row=2, column=0, sticky="w")
        ttk.Entry(root, textvariable=self.path_var).grid(row=2, column=1, sticky="ew", padx=8)
        ttk.Button(root, text="参照…", command=self._pick).grid(row=2, column=2)
        ttk.Checkbutton(root, text="Dry Run（変更を加えず計画だけ確認）", variable=self.dry_run_var).grid(row=3, column=0, columnspan=3, sticky="w", pady=12)
        self.run_button = ttk.Button(root, text="ワークフローを実行", command=self._run)
        self.run_button.grid(row=4, column=0, sticky="w")
        ttk.Label(root, textvariable=self.status_var, wraplength=720).grid(row=4, column=1, columnspan=2, sticky="w", padx=10)
        self.output = tk.Text(root, height=16, wrap="word", state="disabled")
        self.output.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(12, 0))
        root.rowconfigure(5, weight=1)

    def _pick(self) -> None:
        path = filedialog.askopenfilename(parent=self, filetypes=[("JSON", "*.json")])
        if path:
            self.path_var.set(path)

    def _run(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        path = self.path_var.get().strip()
        if not path:
            messagebox.showinfo("設定が必要です", "ワークフローJSONを選択してください。", parent=self)
            return
        try:
            config = load_workflow(path)
            steps = config.get("workflow")
            if not isinstance(steps, list) or not steps:
                raise ValueError("workflowは1件以上のステップを含む必要があります。")
        except Exception as exc:
            self.status_var.set(f"設定エラー: {exc}")
            return
        dry_run = self.dry_run_var.get()
        if not dry_run and not messagebox.askokcancel("実行前の確認", f"{len(steps)}個の操作を実行します。ファイル変更やHTTP呼び出しが発生する場合があります。設定内容を確認しましたか？", parent=self):
            return
        self.run_button.config(state="disabled")
        self.status_var.set("処理中…")
        self.worker = threading.Thread(target=self._worker, args=(path, dry_run), daemon=True)
        self.worker.start()

    def _worker(self, path: str, dry_run: bool) -> None:
        try:
            result = execute_workflow(path, dry_run=dry_run)
            self.events.put(("ok", result or "完了しました。"))
        except Exception as exc:
            self.events.put(("error", f"{type(exc).__name__}: {exc}"))

    def _poll(self) -> None:
        try:
            while True:
                kind, text = self.events.get_nowait()
                self.status_var.set("完了" if kind == "ok" else "エラー: 処理を完了できませんでした。")
                self.output.config(state="normal")
                self.output.insert("end", text + "\n")
                self.output.see("end")
                self.output.config(state="disabled")
                self.run_button.config(state="normal")
        except queue.Empty:
            pass
        self.after(100, self._poll)


if __name__ == "__main__":
    WorkflowGui().mainloop()
