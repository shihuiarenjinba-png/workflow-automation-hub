"""Deterministic file-based triggers and conditions for local workflows."""
from __future__ import annotations

from pathlib import Path
from typing import Any


class RuleError(ValueError):
    pass


def _file(base_dir: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise RuleError("A valid local file path is required")
    root = base_dir.expanduser().resolve()
    candidate = (root / value).resolve()
    if not candidate.is_relative_to(root) or candidate == root:
        raise RuleError("File trigger/condition path is outside working folder")
    return candidate


def _evaluate(base: Path, condition: dict[str, Any]) -> bool:
    if not isinstance(condition, dict):
        raise RuleError("Trigger/condition must be an object")
    kind = condition.get("type")
    if kind == "manual":
        return True
    if kind == "file_exists":
        return _file(base, condition.get("path")).is_file()
    if kind == "extension_is":
        file = _file(base, condition.get("path"))
        extension = condition.get("extension")
        if not isinstance(extension, str) or not extension.startswith(".") or len(extension) > 20:
            raise RuleError("Extension condition requires .csv or another explicit suffix")
        return file.is_file() and file.suffix.lower() == extension.lower()
    if kind == "text_contains":
        file = _file(base, condition.get("path"))
        needle = condition.get("text")
        if not isinstance(needle, str) or not needle or len(needle) > 200:
            raise RuleError("Text condition must contain 1 to 200 characters")
        if not file.is_file():
            return False
        if file.stat().st_size > 1_000_000:
            raise RuleError("Text condition input exceeds 1 MiB")
        try:
            return needle in file.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise RuleError("Text condition requires a UTF-8 file") from exc
    raise RuleError("Unsupported trigger/condition type")


def evaluate_rules(config: dict[str, Any], base_dir: Path) -> tuple[bool, str]:
    trigger = config.get("trigger", {"type": "manual"})
    if not _evaluate(base_dir, trigger):
        return False, "trigger_not_met"
    conditions = config.get("conditions", [])
    if not isinstance(conditions, list):
        raise RuleError("conditions must be a list")
    for index, condition in enumerate(conditions, 1):
        if not _evaluate(base_dir, condition):
            return False, f"condition_{index}_not_met"
    return True, "eligible"
