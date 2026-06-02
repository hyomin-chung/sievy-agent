import pytest
from unittest.mock import MagicMock, patch
from connectors.base import PostCandidate


@pytest.fixture
def post():
    return PostCandidate(
        post_id="935227",
        title="벨뷰 룸 렌트합니다",
        url="https://kseattle.com/?uid=935227",
    )


def test_fetch_body_returns_markdown(post):
    with patch("agents.detail_fetch_agent.FirecrawlConnector") as mock_connector_class:
        mock_connector = MagicMock()
        mock_connector.fetch_detail.return_value = (
            "# 벨뷰 룸 렌트\n\n월 $950, 6월 입주 가능"
        )
        mock_connector_class.return_value = mock_connector

        from agents.detail_fetch_agent import fetch_body

        result = fetch_body(post.url)

        assert "body" in result
        assert "$950" in result["body"]


def test_fetch_images_extracts_urls():
    from agents.detail_fetch_agent import fetch_images

    body = "본문 내용\n![공고이미지](https://example.com/image.jpg)\n더 많은 내용"
    result = fetch_images(body)

    assert "image_urls" in result
    assert "https://example.com/image.jpg" in result["image_urls"]


def test_fetch_images_returns_empty_when_no_images():
    from agents.detail_fetch_agent import fetch_images

    body = "이미지 없는 본문입니다."
    result = fetch_images(body)

    assert result["image_urls"] == []


def test_fetch_body_returns_error_on_failure():
    with patch("agents.detail_fetch_agent.FirecrawlConnector") as mock_connector_class:
        mock_connector_class.side_effect = Exception("API error")

        from agents.detail_fetch_agent import fetch_body

        result = fetch_body("https://example.com/post/1")

        assert "error" in result
        assert result["body"] == ""
