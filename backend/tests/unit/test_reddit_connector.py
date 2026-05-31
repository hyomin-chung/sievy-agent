import pytest
from unittest.mock import MagicMock, patch
from connectors.reddit import RedditConnector
from connectors.base import PostCandidate
from datetime import datetime

MOCK_LISTING = {
    "data": {
        "children": [
            {
                "data": {
                    "id": "abc123",
                    "title": "Room for rent in Bellevue",
                    "permalink": "/r/Seattle/comments/abc123/room_for_rent/",
                    "created_utc": 1748736000.0,
                }
            },
            {
                "data": {
                    "id": "def456",
                    "title": "Roommate wanted in Redmond",
                    "permalink": "/r/Seattle/comments/def456/roommate_wanted/",
                    "created_utc": 1748649600.0,
                }
            },
        ]
    }
}

MOCK_DETAIL = [
    {
        "data": {
            "children": [
                {
                    "data": {
                        "title": "Room for rent in Bellevue",
                        "selftext": "2br/1ba, $1200/month, available June 1.",
                    }
                }
            ]
        }
    }
]


@pytest.fixture
def connector():
    return RedditConnector()


def test_fetch_listing_returns_post_candidates(connector):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_LISTING
    mock_response.raise_for_status = MagicMock()

    with patch("connectors.reddit.httpx.get", return_value=mock_response):
        posts = connector.fetch_listing("https://www.reddit.com/r/Seattle")

    assert len(posts) == 2
    assert all(isinstance(p, PostCandidate) for p in posts)
    assert posts[0].post_id == "t3_abc123"
    assert posts[0].title == "Room for rent in Bellevue"
    assert "reddit.com" in posts[0].url
    assert isinstance(posts[0].date, datetime)


def test_fetch_detail_returns_body(connector):
    post = PostCandidate(
        post_id="t3_abc123",
        title="Room for rent in Bellevue",
        url="https://www.reddit.com/r/Seattle/comments/abc123/room_for_rent/",
    )

    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_DETAIL
    mock_response.raise_for_status = MagicMock()

    with patch("connectors.reddit.httpx.get", return_value=mock_response):
        body = connector.fetch_detail(post)

    assert "Room for rent in Bellevue" in body
    assert "$1200/month" in body


def test_extract_post_id_from_url(connector):
    url = "https://www.reddit.com/r/Seattle/comments/abc123/room_for_rent/"
    post_id = connector.extract_post_id(url)
    assert post_id == "t3_abc123"


def test_extract_post_id_fallback(connector):
    url = "https://www.reddit.com/r/Seattle/"
    post_id = connector.extract_post_id(url)
    assert len(post_id) == 16


def test_to_json_url(connector):
    url = "https://www.reddit.com/r/Seattle"
    json_url = connector._to_json_url(url)
    assert json_url.endswith("/new.json")
