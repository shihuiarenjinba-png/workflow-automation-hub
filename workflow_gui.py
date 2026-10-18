"""Visual Trigger -> Condition -> Action editor for safe local workflows."""
import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from workflow_hub import Runner
from workflow_rules import evaluate_rules


class WorkflowWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.pack(fill="both", expand=True)
        self.base = tk.StringVar(value=str(Path.home() / "WorkflowAutomation"))
        self.hosts = tk.StringVar(value="example.com")
        self.trigger = tk.StringVar(value="manual")
        self.trigger_path = tk.StringVar()
        self.condition = tk.StringVar(value="none")
        self.condition_path = tk.StringVar()
        self.condition_text = tk.StringVar()
        self.action = tk.StringVar(value="copy_file")
        self.target = tk.StringVar()
        self.value = tk.StringVar()
        self.status = tk.StringVar(value="Set a trigger, conditions and actions.")
        self.steps = []
        self.columnconfigure(1, weight=1)
        self.rowconfigure(10, weight=1)
        self._field(0, "Working folder", self.base)
        self._field(1, "Allowed HTTPS API hosts (comma separated)", self.hosts)
        ttk.Button(self, text="Browse", command=self.browse).grid(row=0, column=2)
        ttk.Label(self, text="Trigger").grid(row=2, column=0, sticky="w")
        ttk.Combobox(self, textvariable=self.trigger, values=("manual", "file_exists"),
                     state="readonly").grid(row=2, column=1, sticky="w")
        self._field(3, "Trigger file (if file_exists)", self.trigger_path)
        ttk.Label(self, text="Condition").grid(row=4, column=0, sticky="w")
        ttk.Combobox(self, textvariable=self.condition,
                     values=("none", "file_exists", "extension_is", "text_contains"),
                     state="readonly").grid(row=4, column=1, sticky="w")
        self._field(5, "Condition file path", self.condition_path)
        self._field(6, "Condition text / extension", self.condition_text)
        ttk.Label(self, text="Action").grid(row=7, column=0, sticky="w")
        ttk.Combobox(self, textvariable=self.action,
                     values=("copy_file", "move_file", "write_text", "http_request"),
                     state="readonly").grid(row=7, column=1, sticky="w")
        self._field(8, "Source path / text output path / HTTPS URL", self.target)
        self._field(9, "Destination path / text content", self.value)
        ttk.Button(self, text="Add action", command=self.add).grid(row=9, column=2)
        self.items = tk.Listbox(self, height=7, exportselection=False)
        self.items.grid(row=10, column=0, columnspan=3, sticky="nsew")
        controls = ttk.Frame(self)
        controls.grid(row=11, column=0, columnspan=3, sticky="w", pady=7)
        for title, callback in (("Remove action", self.remove), ("Load", self.load),
                                ("Save", self.save), ("Preview", self.preview),
                                ("Run once", self.execute)):
            ttk.Button(controls, text=title, command=callback).pack(side="left", padx=3)
        ttk.Label(self, textvariable=self.status, wraplength=780).grid(
            row=12, column=0, columnspan=3, sticky="w")

    def _field(self, row, label, variable):
        ttk.Label(self, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Entry(self, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=3)

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.base.set(path)

    def add(self):
        action, target, value = self.action.get(), self.target.get().strip(), self.value.get()
        if not target or (action in ("copy_file", "move_file") and not value.strip()):
            messagebox.showerror("Invalid action", "Source/URL and any required destination are missing")
            return
        if action in ("copy_file", "move_file"):
            step = {"action": action, "src": target, "dst": value.strip(), "overwrite": False}
        elif action == "write_text":
            step = {"action": action, "path": target, "text": value, "overwrite": False}
        else:
            step = {"action": action, "url": target, "method": "GET"}
        self.steps.append(step)
        self.refresh()

    def refresh(self):
        self.items.delete(0, "end")
        for step in self.steps:
            self.items.insert("end", json.dumps(step, ensure_ascii=False))

    def remove(self):
        selected = self.items.curselection()
        if selected:
            self.steps.pop(selected[0])
            self.refresh()

    def config(self):
        if not self.steps:
            raise ValueError("At least one action is required")
        if self.trigger.get() == "file_exists":
            trigger = {"type": "file_exists", "path": self.trigger_path.get().strip()}
        else:
            trigger = {"type": "manual"}
        conditions = []
        if self.condition.get() != "none":
            condition = {"type": self.condition.get(), "path": self.condition_path.get().strip()}
            if self.condition.get() == "text_contains":
                condition["text"] = self.condition_text.get()
            if self.condition.get() == "extension_is":
                condition["extension"] = self.condition_text.get().strip()
            conditions.append(condition)
        cfg = {"base_dir": str(Path(self.base.get()).expanduser().resolve()),
               "allow_hosts": [h.strip().lower() for h in self.hosts.get().split(",") if h.strip()],
               "trigger": trigger, "conditions": conditions, "workflow": list(self.steps)}
        Runner(cfg, dry_run=True).run()
        return cfg

    def preview(self):
        try:
            cfg = self.config()
            yes, reason = evaluate_rules(cfg, Path(cfg["base_dir"]))
            self.status.set(f"Preview: {len(cfg['workflow'])} steps, trigger/condition: {reason}. No changes made.")
        except Exception as exc:
            messagebox.showerror("Validation failed", str(exc))

    def save(self):
        try:
            cfg = self.config()
            path = filedialog.asksaveasfilename(defaultextension=".json")
            if path:
                with Path(path).open("x", encoding="utf-8") as stream:
                    json.dump(cfg, stream, ensure_ascii=False, indent=2)
                self.status.set("Saved " + path)
        except Exception as exc:
            messagebox.showerror("Not saved", str(exc))

    def load(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            cfg = json.loads(Path(path).read_text(encoding="utf-8"))
            Runner(cfg, dry_run=True).run()
            self.base.set(cfg["base_dir"])
            self.hosts.set(",".join(cfg.get("allow_hosts", [])))
            self.trigger.set(cfg.get("trigger", {"type": "manual"})["type"])
            self.trigger_path.set(cfg.get("trigger", {}).get("path", ""))
            cond = cfg.get("conditions", [])
            self.condition.set(cond[0]["type"] if cond else "none")
            self.condition_path.set(cond[0].get("path", "") if cond else "")
            self.condition_text.set((cond[0].get("text") or cond[0].get("extension") or "") if cond else "")
            self.steps = list(cfg["workflow"])
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Cannot load", str(exc))

    def execute(self):
        try:
            cfg = self.config()
            yes, reason = evaluate_rules(cfg, Path(cfg["base_dir"]))
            if not yes:
                self.status.set("Not executed: " + reason)
                return
        except Exception as exc:
            messagebox.showerror("Invalid workflow", str(exc))
            return
        if not messagebox.askyesno("Run", "Execute these file/API actions now?"):
            return
        self.status.set("Running...")
        def work():
            try:
                Runner(cfg).run()
                self.after(0, self.status.set, "Run completed.")
            except Exception as exc:
                self.after(0, self.status.set, "Run failed: " + type(exc).__name__)
        threading.Thread(target=work, daemon=True).start()


def main():
    root = tk.Tk()
    root.title("Workflow Automation Hub")
    root.minsize(850, 620)
    WorkflowWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
