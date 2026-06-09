from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Alert:
    watch_id: str
    user_id: str
    post_id: str
    post_url: str
    title: str
    verdict: str
    extracted_fields: dict[str, Any]
    summary: str
    alert_id: str = ""
    is_read: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "alert_id": self.alert_id,
            "watch_id": self.watch_id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "post_url": self.post_url,
            "title": self.title,
            "verdict": self.verdict,
            "extracted_fields": self.extracted_fields,
            "summary": self.summary,
            "is_read": self.is_read,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Alert":
        return cls(
            alert_id=data.get("alert_id", ""),
            watch_id=data["watch_id"],
            user_id=data["user_id"],
            post_id=data["post_id"],
            post_url=data["post_url"],
            title=data["title"],
            verdict=data["verdict"],
            extracted_fields=data.get("extracted_fields", {}),
            summary=data.get("summary", ""),
            is_read=data.get("is_read", False),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
        )
