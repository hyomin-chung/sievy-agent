from connectors.base import AbstractConnector, PostCandidate


class FeedDetector:
    def create_baseline(
        self,
        connector: AbstractConnector,
        url: str,
        url_pattern: dict | None = None,
    ) -> set[str]:
        posts = connector.fetch_listing(url, page=1, url_pattern=url_pattern)
        return {post.post_id for post in posts}

    def detect_new_posts(
        self,
        connector: AbstractConnector,
        url: str,
        baseline_post_ids: set[str],
        url_pattern: dict | None = None,
    ) -> list[PostCandidate]:
        posts = connector.fetch_listing(url, page=1, url_pattern=url_pattern)
        return [post for post in posts if post.post_id not in baseline_post_ids]
