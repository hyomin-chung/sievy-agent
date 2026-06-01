from connectors.base import AbstractConnector, PostCandidate
from config import config

MAX_PAGES = config.MAX_PAGES


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
        """
        Scan listing pages and return only posts not in baseline.
        Stops early when a baseline post is found or MAX_PAGES is reached.
        """
        new_posts = []

        for page in range(1, MAX_PAGES + 1):
            try:
                posts = connector.fetch_listing(url, page=page)
            except NotImplementedError:
                break

            if not posts:
                break

            found_baseline = False
            for post in posts:
                if post.post_id in baseline_post_ids:
                    found_baseline = True
                    break
                new_posts.append(post)

            if found_baseline:
                break

        return new_posts
