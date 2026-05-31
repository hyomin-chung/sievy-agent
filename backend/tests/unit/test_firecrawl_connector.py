import pytest
from unittest.mock import MagicMock, patch
from connectors.firecrawl_connector import FirecrawlConnector
from connectors.base import PostCandidate

MOCK_LISTING_RESULT = {
    "markdown": "# K-Seattle Rent Board\n\nSome content",
    "links": [
        "https://kseattle.com/rentlodge/?uid=935227&mod=document",
        "https://kseattle.com/rentlodge/?uid=935228&mod=document",
        "https://kseattle.com/rentlodge/",
    ],
}

MOCK_DETAIL_RESULT = {
    "markdown": "## 벨뷰 별체 렌트 합니다\n\n월 $950, 6월 1일 입주 가능"
}


@pytest.fixture
def connector():
    with patch("connectors.firecrawl_connector.FirecrawlApp") as mock_app_class:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        yield FirecrawlConnector(api_key="fc-test-key"), mock_app


def test_fetch_listing_returns_post_candidates(connector):
    fc, mock_app = connector
    mock_app.scrape_url.return_value = MOCK_LISTING_RESULT

    posts = fc.fetch_listing("https://kseattle.com/rentlodge/")

    assert len(posts) == 3
    assert all(isinstance(p, PostCandidate) for p in posts)
    assert posts[0].post_id == "935227"
    assert posts[1].post_id == "935228"


def test_fetch_detail_returns_markdown(connector):
    fc, mock_app = connector
    mock_app.scrape_url.return_value = MOCK_DETAIL_RESULT

    post = PostCandidate(
        post_id="935227",
        title="벨뷰 별체 렌트 합니다",
        url="https://kseattle.com/rentlodge/?uid=935227&mod=document",
    )
    body = fc.fetch_detail(post)

    assert "벨뷰" in body
    assert "$950" in body


def test_extract_post_id_from_uid_param(connector):
    fc, _ = connector
    url = "https://kseattle.com/rentlodge/?uid=935227&mod=document"
    assert fc.extract_post_id(url) == "935227"


def test_extract_post_id_from_path_segment(connector):
    fc, _ = connector
    url = "https://example.com/posts/12345"
    assert fc.extract_post_id(url) == "12345"


def test_extract_post_id_hash_fallback(connector):
    fc, _ = connector
    url = "https://kseattle.com/rentlodge/"
    post_id = fc.extract_post_id(url)
    assert len(post_id) == 16
