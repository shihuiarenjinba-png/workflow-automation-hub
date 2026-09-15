from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ScheduleSpec:
    kind: str = "daily"
    time: str = "08:00"
    weekdays: list[str] = field(default_factory=lambda: ["MON", "TUE", "WED", "THU", "FRI"])

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> "ScheduleSpec":
        raw = raw or {}
        return cls(
            kind=str(raw.get("kind", "daily")),
            time=str(raw.get("time", "08:00")),
            weekdays=[str(x).upper() for x in raw.get("weekdays", ["MON", "TUE", "WED", "THU", "FRI"])],
        )


@dataclass
class BloggerLinkJob:
    id: str
    name: str
    blog_id: str
    target_text: str
    link_url: str
    anchor_text: str
    max_posts: int = 50
    status: str = "LIVE"
    enabled: bool = True
    schedule: ScheduleSpec = field(default_factory=ScheduleSpec)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "BloggerLinkJob":
        return cls(
            id=str(raw["id"]),
            name=str(raw.get("name", raw["id"])),
            blog_id=str(raw["blog_id"]),
            target_text=str(raw["target_text"]),
            link_url=str(raw["link_url"]),
            anchor_text=str(raw.get("anchor_text") or raw["target_text"]),
            max_posts=max(1, min(int(raw.get("max_posts", 50)), 500)),
            status=str(raw.get("status", "LIVE")).upper(),
            enabled=bool(raw.get("enabled", True)),
            schedule=ScheduleSpec.from_dict(raw.get("schedule")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
