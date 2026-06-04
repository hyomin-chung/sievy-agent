from unittest.mock import MagicMock, patch
from connectors.base import PostCandidate


def make_post(post_id: str) -> PostCandidate:
    return PostCandidate(
        post_id=post_id,
        title=f"Post {post_id}",
        url=f"https://example.com/{post_id}",
    )


def test_fetch_post_content_returns_body():
    with patch("feed.detail_fetcher.FirecrawlConnector") as mock_connector_class:
        mock_connector = MagicMock()
        mock_connector.fetch_detail.return_value = "Bellevue room $950/month"
        mock_connector_class.return_value = mock_connector

        from feed.detail_fetcher import fetch_post_content

        post = make_post("001")
        result = fetch_post_content(post)

        assert "$950" in result


def test_fetch_post_content_returns_empty_on_failure():
    with patch("feed.detail_fetcher.FirecrawlConnector") as mock_connector_class:
        mock_connector = MagicMock()
        mock_connector.fetch_detail.return_value = ""
        mock_connector_class.return_value = mock_connector

        from feed.detail_fetcher import fetch_post_content

        post = make_post("001")
        result = fetch_post_content(post)

        assert result == ""
