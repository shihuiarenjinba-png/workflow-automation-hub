from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import audit_log_path


class AuditLogger:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or audit_log_path()

    def write(self, event: str, **fields: Any) -> None:
        row = {"ts": datetime.now(timezone.utc).isoformat(), "event": event, **fields}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
