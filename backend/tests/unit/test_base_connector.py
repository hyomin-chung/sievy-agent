import pytest
from datetime import datetime
from connectors.base import AbstractConnector, PostCandidate


class ConcreteConnector(AbstractConnector):
    def fetch_listing(self, url: str, page: int = 1) -> list[PostCandidate]:
        return [PostCandidate(post_id="1", title="Test", url=url)]

    def fetch_detail(self, post: PostCandidate) -> str:
        return "Test body"

    def extract_post_id(self, url: str) -> str:
        return "1"


def test_post_candidate_fields():
    post = PostCandidate(post_id="123", title="Test", url="https://example.com")
    assert post.post_id == "123"
    assert post.title == "Test"
    assert post.url == "https://example.com"
    assert post.date is None


def test_post_candidate_with_date():
    now = datetime.now()
    post = PostCandidate(
        post_id="123", title="Test", url="https://example.com", date=now
    )
    assert post.date == now


def test_abstract_connector_cannot_be_instantiated():
    with pytest.raises(TypeError):
        AbstractConnector()


def test_concrete_connector_fetch_listing():
    connector = ConcreteConnector()
    posts = connector.fetch_listing("https://example.com")
    assert len(posts) == 1
    assert posts[0].post_id == "1"


def test_concrete_connector_fetch_detail():
    connector = ConcreteConnector()
    post = PostCandidate(post_id="1", title="Test", url="https://example.com")
    body = connector.fetch_detail(post)
    assert body == "Test body"


def test_concrete_connector_extract_post_id():
    connector = ConcreteConnector()
    post_id = connector.extract_post_id("https://example.com/post/1")
    assert post_id == "1"
