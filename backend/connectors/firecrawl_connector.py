import hashlib
from urllib.parse import urlparse, parse_qs

from firecrawl import Firecrawl

from config import FIRECRAWL_API_KEY
from connectors.base import AbstractConnector, PostCandidate
from urllib.parse import unquote


class FirecrawlConnector(AbstractConnector):
    def __init__(self, api_key: str | None = None):
        self.app = Firecrawl(api_key=api_key or FIRECRAWL_API_KEY)

    def fetch_listing(self, url: str, page: int = 1) -> list[PostCandidate]:
        if page != 1:
            raise NotImplementedError(
                "FirecrawlConnector does not support pagination beyond page 1."
            )

        result = self.app.scrape(url, formats=["markdown", "links"])
        links = (
            result.get("links", [])
            if isinstance(result, dict)
            else (getattr(result, "links", None) or [])
        )

        parsed_source = urlparse(url)
        source_path = unquote(parsed_source.path.rstrip("/"))
        seen = set()
        candidates = []

        id_params = ["uid", "id", "no", "idx", "seq", "article_id", "post_id", "num"]

        for link in links:
            parsed = urlparse(link)

            if parsed.netloc != parsed_source.netloc:
                continue

            link_path = unquote(parsed.path.rstrip("/"))

            if not link_path.startswith(source_path):
                continue

            params = parse_qs(parsed.query)

            if link_path == source_path:
                matched_key = next((k for k in id_params if k in params), None)
                if not matched_key:
                    continue
                post_id = params[matched_key][0]
            else:
                path_parts = link_path.split("/")
                last = path_parts[-1] if path_parts else ""
                if last.isdigit():
                    post_id = last
                else:
                    matched_key = next((k for k in id_params if k in params), None)
                    if matched_key:
                        post_id = params[matched_key][0]
                    else:
                        continue

            if post_id in seen:
                continue
            seen.add(post_id)

            candidates.append(
                PostCandidate(
                    post_id=post_id,
                    title="",
                    url=link,
                )
            )

        return candidates

    def fetch_detail(self, post: PostCandidate) -> str:
        result = self.app.scrape(post.url, formats=["markdown"], only_main_content=True)
        if isinstance(result, dict):
            return result.get("markdown", "")
        return getattr(result, "markdown", None) or ""

    def extract_post_id(self, url: str) -> str:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        id_params = ["uid", "id", "no", "idx", "seq", "article_id", "post_id", "num"]
        for key in id_params:
            if key in params:
                return params[key][0]

        path_parts = parsed.path.rstrip("/").split("/")
        if path_parts and path_parts[-1].isdigit():
            return path_parts[-1]

        return hashlib.sha256(url.encode()).hexdigest()[:16]
