from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Watch:
    user_id: str
    source_url: str
    category: str
    criteria: dict[str, Any]
    baseline_post_ids: list[str] = field(default_factory=list)
    watch_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_scanned_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "watch_id": self.watch_id,
            "user_id": self.user_id,
            "source_url": self.source_url,
            "category": self.category,
            "criteria": self.criteria,
            "baseline_post_ids": self.baseline_post_ids,
            "created_at": self.created_at,
            "last_scanned_at": self.last_scanned_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Watch":
        return cls(
            watch_id=data.get("watch_id", ""),
            user_id=data["user_id"],
            source_url=data["source_url"],
            category=data["category"],
            criteria=data.get("criteria", {}),
            baseline_post_ids=data.get("baseline_post_ids", []),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
            last_scanned_at=data.get("last_scanned_at"),
        )
