import pytest
from unittest.mock import MagicMock
from feed.detail_fetcher import DetailFetcher
from connectors.base import PostCandidate


def make_post(post_id: str) -> PostCandidate:
    return PostCandidate(
        post_id=post_id,
        title=f"Post {post_id}",
        url=f"https://example.com/{post_id}",
    )


@pytest.fixture
def fetcher():
    return DetailFetcher()


def test_fetch_returns_post_body_tuples(fetcher):
    connector = MagicMock()
    connector.fetch_detail.side_effect = [
        "Bellevue room $950/month available June 1",
        "Redmond apartment $800/month",
    ]

    posts = [make_post("001"), make_post("002")]
    results = fetcher.fetch(connector, posts)

    assert len(results) == 2
    assert results[0][0].post_id == "001"
    assert "$950" in results[0][1]
    assert results[1][0].post_id == "002"
    assert "$800" in results[1][1]


def test_fetch_skips_empty_body(fetcher):
    connector = MagicMock()
    connector.fetch_detail.side_effect = [
        "Bellevue room $950/month",
        "",
        "   ",
    ]

    posts = [make_post("001"), make_post("002"), make_post("003")]
    results = fetcher.fetch(connector, posts)

    assert len(results) == 1
    assert results[0][0].post_id == "001"


def test_fetch_empty_posts(fetcher):
    connector = MagicMock()
    results = fetcher.fetch(connector, [])
    assert results == []
