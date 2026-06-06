import hashlib
import json
import re
from urllib.parse import urlparse, parse_qs, unquote

from firecrawl import Firecrawl
from google import genai

from config import FIRECRAWL_API_KEY, GOOGLE_API_KEY, GEMINI_MODEL
from connectors.base import AbstractConnector, PostCandidate


def _extract_links_from_result(result) -> tuple[list[str], str]:
    if isinstance(result, dict):
        links = result.get("links", []) or []
        markdown = result.get("markdown", "") or ""
    else:
        links = getattr(result, "links", None) or []
        markdown = getattr(result, "markdown", "") or ""

    if not links and markdown:
        links = re.findall(r"\[.*?\]\((https?://[^\)]+)\)", markdown)
        links = [re.split(r'\s+"', u)[0].strip() for u in links]

    links = [
        l.split("#")[0].rstrip("/") + ("/" if l.split("#")[0].endswith("/") else "")
        for l in links
        if l.split("#")[0]
    ]
    links = list(dict.fromkeys(links))

    return links, markdown


class FirecrawlConnector(AbstractConnector):
    def __init__(self, api_key: str | None = None):
        self.app = Firecrawl(api_key=api_key or FIRECRAWL_API_KEY)

    def detect_post_url_pattern(self, url: str) -> dict:
        result = self.app.scrape(
            url, formats=["markdown", "links"], only_main_content=False
        )
        links, _ = _extract_links_from_result(result)
        sample = links[:100]

        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"""You are analyzing a listing page to identify the URL pattern for individual posts.

Source listing URL: {url}

Links found on this page (sample of up to 100):
{chr(10).join(sample)}

The source URL is the listing/index page. Individual post URLs will have ADDITIONAL parameters or path segments not present in the source URL.

Return a JSON object with ONE of these formats:

1. Query parameter that exists in post URLs but NOT in the source URL:
   {{"type": "query_param", "key": "parm_bod_uid"}}

2. Path regex pattern:
   {{"type": "path_regex", "pattern": "/see/.+/\\d+\\\\.html$"}}

3. Path depth (slug-based):
   {{"type": "path_depth", "min_depth": 2}}

4. Base36 ID segment:
   {{"type": "base36", "segment": "comments"}}

5. UTM source pattern (e.g. MLH events: utm_source=mlh&utm_campaign=events):
   {{"type": "utm_source", "value": "mlh", "campaign": "events"}}
   Use this when listing page links to external sites via UTM tracking parameters.
   Only include "campaign" if all post links share the same utm_campaign value.

Return ONLY the JSON object. No explanation, no markdown, no backticks.""",
        )

        text = re.sub(r"```json|```", "", (response.text or "{}")).strip()
        try:
            return json.loads(text)
        except Exception:
            return {"type": "path_depth", "min_depth": 2}

    def _matches_pattern(self, link: str, source_url: str, pattern: dict) -> bool:
        parsed_link = urlparse(link)
        parsed_source = urlparse(source_url)
        pattern_type = pattern.get("type")
        params = parse_qs(parsed_link.query)

        if pattern_type == "utm_source":
            value = pattern.get("value", "")
            campaign = pattern.get("campaign", "")
            if params.get("utm_source", [""])[0] != value:
                return False
            if campaign and params.get("utm_campaign", [""])[0] != campaign:
                return False
            return True

        source_domain = parsed_source.netloc
        link_domain = parsed_link.netloc
        base_domain = ".".join(source_domain.split(".")[-2:])
        if link_domain != source_domain and not link_domain.endswith("." + base_domain):
            return False

        link_path = unquote(parsed_link.path)
        source_path = unquote(parsed_source.path.rstrip("/"))

        if pattern_type == "query_param":
            key = pattern.get("key", "")
            if key not in params:
                return False
            source_params = parse_qs(parsed_source.query)
            if key in source_params and source_params[key] == params.get(key):
                return False
            return True

        elif pattern_type == "path_regex":
            pat = pattern.get("pattern", "")
            try:
                return bool(re.search(pat, link_path)) or bool(re.search(pat, link))
            except Exception:
                return False

        elif pattern_type == "path_depth":
            lp = link_path.rstrip("/")
            min_depth = pattern.get("min_depth", 2)
            depth = len([p for p in lp.split("/") if p])
            return depth >= min_depth and lp != source_path

        elif pattern_type == "base36":
            lp = link_path.rstrip("/")
            segment = pattern.get("segment", "")
            parts = lp.split("/")
            if segment in parts:
                idx = parts.index(segment)
                if idx + 1 < len(parts):
                    return bool(re.match(r"^[a-z0-9]{4,12}$", parts[idx + 1]))
            return False

        return False

    def _fallback_filter(self, links: list[str], source_url: str) -> list[str]:
        parsed_source = urlparse(source_url)
        source_path = unquote(parsed_source.path.rstrip("/"))
        id_params = ["uid", "id", "no", "idx", "seq", "article_id", "post_id", "num"]
        result = []

        for link in links:
            parsed = urlparse(link)
            if parsed.netloc != parsed_source.netloc:
                continue
            link_path = unquote(parsed.path.rstrip("/"))
            if not link_path.startswith(source_path):
                continue
            params = parse_qs(parsed.query)
            if link_path == source_path:
                if not any(k in params for k in id_params):
                    continue
            else:
                last = link_path.split("/")[-1] if link_path.split("/") else ""
                if not last.isdigit() and not any(k in params for k in id_params):
                    continue
            result.append(link)

        return result

    def fetch_listing(
        self, url: str, page: int = 1, url_pattern: dict | None = None
    ) -> list[PostCandidate]:
        if page != 1:
            raise NotImplementedError(
                "FirecrawlConnector does not support pagination beyond page 1."
            )

        result = self.app.scrape(
            url, formats=["markdown", "links"], only_main_content=False
        )
        links, _ = _extract_links_from_result(result)

        if url_pattern:
            filtered = [l for l in links if self._matches_pattern(l, url, url_pattern)]
            if not filtered:
                filtered = self._fallback_filter(links, url)
        else:
            filtered = self._fallback_filter(links, url)

        seen = set()
        candidates = []
        for link in filtered:
            post_id = self.extract_post_id(link)
            if post_id in seen:
                continue
            seen.add(post_id)
            candidates.append(PostCandidate(post_id=post_id, title="", url=link))

        return candidates

    def fetch_detail(self, post: PostCandidate) -> str:
        result = self.app.scrape(
            post.url,
            formats=["markdown"],
            only_main_content=True,
            remove_base64_images=True,
            block_ads=True,
            max_age=0,
        )
        if isinstance(result, dict):
            return result.get("markdown", "")
        return getattr(result, "markdown", "") or ""

    def extract_post_id(self, url: str) -> str:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        for key in ["uid", "id", "no", "idx", "seq", "article_id", "post_id", "num"]:
            if key in params:
                return params[key][0]

        for part in reversed(parsed.path.rstrip("/").split("/")):
            clean = re.sub(r"\.(html?|php|asp|jsp)$", "", part)
            if clean.isdigit():
                return clean
            if re.match(r"^[a-z0-9]{4,12}$", clean) and not clean.isalpha():
                return clean
            m = re.match(r"^(\d{5,})", clean)
            if m:
                return m.group(1)

        return hashlib.sha256(url.encode()).hexdigest()[:16]
