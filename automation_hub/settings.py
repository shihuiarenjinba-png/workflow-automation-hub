from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .paths import settings_path

DEFAULTS: dict[str, Any] = {"locale": "ja", "google_credentials_file": ""}


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or settings_path()

    def load(self) -> dict[str, Any]:
        data = dict(DEFAULTS)
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                data.update(raw)
        return data

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(data, ensure_ascii=False, indent=2)
        fd, temp_name = tempfile.mkstemp(prefix="settings-", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(payload)
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
