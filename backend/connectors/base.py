from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PostCandidate:
    post_id: str
    title: str
    url: str
    date: datetime | None = None


class AbstractConnector(ABC):
    @abstractmethod
    def fetch_listing(self, url: str, page: int = 1) -> list[PostCandidate]:
        """Fetch post candidates from a listing page."""

    @abstractmethod
    def fetch_detail(self, post: PostCandidate) -> str:
        """Fetch and return clean body text of a single post."""

    @abstractmethod
    def extract_post_id(self, url: str) -> str:
        """Generate a stable post_id from a URL."""
