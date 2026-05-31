import pytest
from unittest.mock import MagicMock, patch
from store.post_store import PostStore
from connectors.base import PostCandidate
from judge.judge_agent import JudgeResult


@pytest.fixture
def store():
    with (
        patch("store.post_store.get_elastic_client") as mock_client_fn,
        patch("store.post_store.ensure_index"),
    ):
        mock_client = MagicMock()
        mock_client_fn.return_value = mock_client
        yield PostStore(), mock_client


def test_is_duplicate_returns_true_when_post_exists(store):
    post_store, mock_client = store
    mock_client.search.return_value = {"hits": {"total": {"value": 1}}}

    assert post_store.is_duplicate("watch_001", "935227") is True


def test_is_duplicate_returns_false_when_post_not_exists(store):
    post_store, mock_client = store
    mock_client.search.return_value = {"hits": {"total": {"value": 0}}}

    assert post_store.is_duplicate("watch_001", "935228") is False


def test_index_post_calls_elastic_index(store):
    post_store, mock_client = store

    post = PostCandidate(
        post_id="935227",
        title="벨뷰 룸 렌트합니다",
        url="https://kseattle.com/?uid=935227",
    )
    judge_result = JudgeResult(
        verdict="worth_checking",
        extracted_fields={"location": "Bellevue", "rent": 950},
        verdict_reason="Location and rent match criteria.",
        summary="A room in Bellevue at $950.",
        confidence="high",
    )

    post_store.index_post(
        watch_id="watch_001",
        post=post,
        body="벨뷰 룸 렌트합니다. 월 $950.",
        category="housing",
        judge_result=judge_result,
    )

    mock_client.index.assert_called_once()
    call_kwargs = mock_client.index.call_args.kwargs
    assert call_kwargs["id"] == "watch_001_935227"
    assert call_kwargs["document"]["verdict"] == "worth_checking"
    assert call_kwargs["document"]["category"] == "housing"
