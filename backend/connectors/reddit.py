import hashlib
from datetime import datetime, timezone

import httpx

from connectors.base import AbstractConnector, PostCandidate

HEADERS = {"User-Agent": "sievy-agent/1.0 (source-bound alert filter)"}


class RedditConnector(AbstractConnector):
    def fetch_listing(self, url: str, page: int = 1) -> list[PostCandidate]:
        api_url = self._to_json_url(url)
        params = {"limit": 25}

        response = httpx.get(api_url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        posts = []

        for child in data["data"]["children"]:
            d = child["data"]
            post_id = f"t3_{d['id']}"
            title = d.get("title", "")
            permalink = f"https://www.reddit.com{d['permalink']}"
            created = datetime.fromtimestamp(d["created_utc"], tz=timezone.utc)

            posts.append(
                PostCandidate(
                    post_id=post_id,
                    title=title,
                    url=permalink,
                    date=created,
                )
            )

        return posts

    def fetch_detail(self, post: PostCandidate) -> str:
        api_url = post.url.rstrip("/") + ".json"

        response = httpx.get(api_url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        data = response.json()
        post_data = data[0]["data"]["children"][0]["data"]
        title = post_data.get("title", "")
        selftext = post_data.get("selftext", "")

        return f"{title}\n\n{selftext}".strip()

    def extract_post_id(self, url: str) -> str:
        parts = url.rstrip("/").split("/")
        for i, part in enumerate(parts):
            if part == "comments" and i + 1 < len(parts):
                return f"t3_{parts[i + 1]}"
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _to_json_url(self, url: str) -> str:
        url = url.rstrip("/")
        if not url.endswith(".json"):
            url += "/new.json"
        return url
