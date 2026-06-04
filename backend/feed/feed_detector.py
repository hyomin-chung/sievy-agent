from connectors.base import AbstractConnector, PostCandidate


class FeedDetector:
    def create_baseline(self, connector: AbstractConnector, url: str) -> set[str]:
        """
        Fetch current posts and return their post_ids as baseline.
        Called once when a user registers a new source.
        """
        posts = connector.fetch_listing(url, page=1)
        return {post.post_id for post in posts}

    def detect_new_posts(
        self,
        connector: AbstractConnector,
        url: str,
        baseline_post_ids: set[str],
    ) -> list[PostCandidate]:
        posts = connector.fetch_listing(url, page=1)
        return [post for post in posts if post.post_id not in baseline_post_ids]
