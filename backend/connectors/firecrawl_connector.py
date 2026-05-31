import hashlib
import os
from urllib.parse import urlparse, parse_qs

from firecrawl import FirecrawlApp

from connectors.base import AbstractConnector, PostCandidate


class FirecrawlConnector(AbstractConnector):
    def __init__(self, api_key: str | None = None):
        self.app = FirecrawlApp(api_key=api_key or os.getenv("FIRECRAWL_API_KEY"))

    def fetch_listing(self, url: str, page: int = 1) -> list[PostCandidate]:
        if page != 1:
            raise NotImplementedError(
                "FirecrawlConnector does not support pagination beyond page 1."
            )

        result = self.app.scrape_url(url, formats=["markdown", "links"])
        links = (
            result.get("links", [])
            if isinstance(result, dict)
            else (getattr(result, "links", None) or [])
        )
        candidates = []

        for link in links:
            post_id = self.extract_post_id(link)
            candidates.append(
                PostCandidate(
                    post_id=post_id,
                    title="",
                    url=link,
                )
            )

        return candidates

    def fetch_detail(self, post: PostCandidate) -> str:
        result = self.app.scrape_url(post.url, formats=["markdown"])
        if isinstance(result, dict):
            return result.get("markdown", "")
        return getattr(result, "markdown", None) or ""

    def extract_post_id(self, url: str) -> str:
        parsed = urlparse(url)

        params = parse_qs(parsed.query)
        if "uid" in params:
            return params["uid"][0]

        path_parts = parsed.path.rstrip("/").split("/")
        last = path_parts[-1] if path_parts else ""
        if last.isdigit():
            return last

        return hashlib.sha256(url.encode()).hexdigest()[:16]
