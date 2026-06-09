from connectors.base import PostCandidate
from connectors.firecrawl_connector import FirecrawlConnector


def fetch_body(url: str) -> str:
    connector = FirecrawlConnector()
    post = PostCandidate(post_id="", title="", url=url)
    return connector.fetch_detail(post)


def fetch_post_content(post: PostCandidate) -> str:
    return fetch_body(post.url)
