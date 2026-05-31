from connectors.base import AbstractConnector, PostCandidate


class DetailFetcher:
    def fetch(
        self,
        connector: AbstractConnector,
        posts: list[PostCandidate],
    ) -> list[tuple[PostCandidate, str]]:
        """
        Fetch body text for each post.
        Returns list of (PostCandidate, body_text) tuples.
        Skips posts where body is empty.
        """
        results = []

        for post in posts:
            body = connector.fetch_detail(post)
            if body.strip():
                results.append((post, body))

        return results
