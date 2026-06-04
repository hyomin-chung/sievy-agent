import pytest
from unittest.mock import MagicMock
from feed.feed_detector import FeedDetector
from connectors.base import PostCandidate


def make_post(post_id: str) -> PostCandidate:
    return PostCandidate(
        post_id=post_id, title=f"Post {post_id}", url=f"https://example.com/{post_id}"
    )


@pytest.fixture
def detector():
    return FeedDetector()


def test_create_baseline_returns_post_ids(detector):
    connector = MagicMock()
    connector.fetch_listing.return_value = [
        make_post("001"),
        make_post("002"),
        make_post("003"),
    ]

    baseline = detector.create_baseline(connector, "https://example.com")

    assert baseline == {"001", "002", "003"}


def test_detect_new_posts_returns_only_new(detector):
    connector = MagicMock()
    connector.fetch_listing.return_value = [
        make_post("004"),
        make_post("005"),
        make_post("001"),  # baseline post
        make_post("002"),
    ]

    new_posts = detector.detect_new_posts(
        connector,
        "https://example.com",
        baseline_post_ids={"001", "002", "003"},
    )

    assert len(new_posts) == 2
    assert new_posts[0].post_id == "004"
    assert new_posts[1].post_id == "005"


def test_detect_new_posts_handles_not_implemented_pagination(detector):
    connector = MagicMock()
    connector.fetch_listing.side_effect = [
        [make_post("004"), make_post("005")],
        NotImplementedError("pagination not supported"),
    ]

    new_posts = detector.detect_new_posts(
        connector,
        "https://example.com",
        baseline_post_ids={"001", "002", "003"},
    )

    assert len(new_posts) == 2


def test_detect_new_posts_empty_listing(detector):
    connector = MagicMock()
    connector.fetch_listing.return_value = []

    new_posts = detector.detect_new_posts(
        connector,
        "https://example.com",
        baseline_post_ids={"001"},
    )

    assert new_posts == []
