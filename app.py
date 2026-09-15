from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from connectors import CONNECTORS, ConnectorError, ConnectorSpec, test_google_connector, test_windows_task_scheduler
from google_auth import AuthError, GoogleAuthStore


class HubApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Private Automation Hub")
        self.geometry("1050x560")
        self.minsize(900, 500)
        self.auth = GoogleAuthStore()
        self.client_file = tk.StringVar()
        self.status_vars: dict[str, tk.StringVar] = {}
        self._build()

    def _build(self) -> None:
        outer = ttk.Frame(self, padding=16)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Private Automation Hub", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="AI判断を使わず、明示設定されたAPIとWindows機能だけを実行します。接続確認は原則として読み取りまたはOAuth検証のみです。",
        ).pack(anchor="w", pady=(4, 14))

        oauth = ttk.LabelFrame(outer, text="Google OAuth（BYOC / 開発・検証用）", padding=10)
        oauth.pack(fill="x", pady=(0, 12))
        ttk.Entry(oauth, textvariable=self.client_file).pack(side="left", fill="x", expand=True)
        ttk.Button(oauth, text="credentials.json を選択", command=self._select_client_file).pack(side="left", padx=(8, 0))

        table = ttk.Frame(outer)
        table.pack(fill="both", expand=True)
        headers = ["接続先", "費用方針", "商用/規約", "注意", "状態", "操作"]
        widths = [18, 27, 14, 38, 16, 26]
        for col, (header, width) in enumerate(zip(headers, widths)):
            label = ttk.Label(table, text=header, font=("Segoe UI", 9, "bold"), width=width)
            label.grid(row=0, column=col, sticky="w", padx=3, pady=4)

        for row_index, spec in enumerate(CONNECTORS.values(), start=1):
            self._add_connector_row(table, row_index, spec)

        scheduler_row = len(CONNECTORS) + 1
        ttk.Label(table, text="Windows Task Scheduler").grid(row=scheduler_row, column=0, sticky="w", padx=3, pady=7)
        ttk.Label(table, text="Windows標準機能 / API料金なし").grid(row=scheduler_row, column=1, sticky="w", padx=3)
        ttk.Label(table, text="ローカル利用").grid(row=scheduler_row, column=2, sticky="w", padx=3)
        ttk.Label(table, text="固定Runnerのみ登録。パスワード保存・任意コマンド登録はしない。").grid(row=scheduler_row, column=3, sticky="w", padx=3)
        var = tk.StringVar(value="未確認")
        self.status_vars["windows_scheduler"] = var
        ttk.Label(table, textvariable=var).grid(row=scheduler_row, column=4, sticky="w", padx=3)
        ttk.Button(table, text="接続確認", command=self._test_scheduler).grid(row=scheduler_row, column=5, sticky="w", padx=3)

        ttk.Label(
            outer,
            text="※ 公開商用版ではBYOCを検証回避目的に使わず、Google OAuthの本番審査・プライバシーポリシー・必要スコープの確認を別途行います。",
            foreground="#555555",
        ).pack(anchor="w", pady=(12, 0))

    def _add_connector_row(self, parent: ttk.Frame, row: int, spec: ConnectorSpec) -> None:
        ttk.Label(parent, text=spec.label).grid(row=row, column=0, sticky="w", padx=3, pady=7)
        ttk.Label(parent, text=spec.cost_note, wraplength=220).grid(row=row, column=1, sticky="w", padx=3)
        ttk.Label(parent, text=spec.commercial_status).grid(row=row, column=2, sticky="w", padx=3)
        ttk.Label(parent, text=spec.risk_note, wraplength=310).grid(row=row, column=3, sticky="w", padx=3)
        var = tk.StringVar(value="接続済み" if self.auth.is_connected(spec.connector_id) else "未接続")
        self.status_vars[spec.connector_id] = var
        ttk.Label(parent, textvariable=var).grid(row=row, column=4, sticky="w", padx=3)

        actions = ttk.Frame(parent)
        actions.grid(row=row, column=5, sticky="w", padx=3)
        ttk.Button(actions, text="接続", command=lambda s=spec: self._connect(s)).pack(side="left")
        ttk.Button(actions, text="接続確認", command=lambda s=spec: self._test(s)).pack(side="left", padx=4)
        ttk.Button(actions, text="解除", command=lambda s=spec: self._disconnect(s)).pack(side="left")

    def _select_client_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Google OAuth client JSON を選択",
            filetypes=[("JSON", "*.json"), ("All files", "*.*")],
        )
        if path:
            self.client_file.set(path)

    def _run_background(self, func, on_success) -> None:
        def worker() -> None:
            try:
                result = func()
            except (AuthError, ConnectorError, OSError, ValueError) as exc:
                self.after(0, lambda: messagebox.showerror("エラー", str(exc)))
                return
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("予期しないエラー", str(exc)))
                return
            self.after(0, lambda: on_success(result))

        threading.Thread(target=worker, daemon=True).start()

    def _connect(self, spec: ConnectorSpec) -> None:
        client_file = self.client_file.get().strip()
        if not client_file:
            messagebox.showwarning("OAuth設定", "先に credentials.json を選択してください。")
            return
        self.status_vars[spec.connector_id].set("認証中...")

        def success(_):
            self.status_vars[spec.connector_id].set("接続済み")
            messagebox.showinfo("接続", f"{spec.label} の認証情報をWindows資格情報ストアに保存しました。")

        self._run_background(lambda: self.auth.connect(spec.connector_id, client_file, list(spec.scopes)), success)

    def _test(self, spec: ConnectorSpec) -> None:
        resource_id: str | None = None
        if spec.resource_prompt:
            resource_id = simpledialog.askstring("接続確認", spec.resource_prompt, parent=self)
            if resource_id is not None:
                resource_id = resource_id.strip() or None
        self.status_vars[spec.connector_id].set("確認中...")

        def task() -> str:
            credentials = self.auth.get(spec.connector_id, list(spec.scopes))
            return test_google_connector(spec, credentials, resource_id)

        def success(message: str) -> None:
            self.status_vars[spec.connector_id].set("接続OK")
            messagebox.showinfo("接続確認", message)

        self._run_background(task, success)

    def _disconnect(self, spec: ConnectorSpec) -> None:
        self.auth.disconnect(spec.connector_id)
        self.status_vars[spec.connector_id].set("未接続")

    def _test_scheduler(self) -> None:
        self.status_vars["windows_scheduler"].set("確認中...")

        def success(message: str) -> None:
            self.status_vars["windows_scheduler"].set("接続OK")
            messagebox.showinfo("接続確認", message)

        self._run_background(test_windows_task_scheduler, success)


if __name__ == "__main__":
    HubApp().mainloop()
