import pytest
from unittest.mock import MagicMock, patch
from store.elastic_store import ElasticStore
from connectors.base import PostCandidate
from judge.judge_agent import JudgeResult


@pytest.fixture
def store():
    with (
        patch("store.elastic_store.get_elastic_client") as mock_client_fn,
        patch("store.elastic_store.ensure_index"),
    ):
        mock_client = MagicMock()
        mock_client_fn.return_value = mock_client
        yield ElasticStore(), mock_client


def test_index_post_calls_elastic_index(store):
    elastic_store, mock_client = store

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

    elastic_store.index_post(
        watch_id="watch_001",
        post=post,
        body="벨뷰 룸 렌트합니다. 월 $950.",
        category="housing",
        judge_result=judge_result,
    )

    mock_client.index.assert_called_once()
    call_kwargs = mock_client.index.call_args.kwargs
    assert call_kwargs["document"]["verdict"] == "worth_checking"
    assert call_kwargs["document"]["category"] == "housing"
