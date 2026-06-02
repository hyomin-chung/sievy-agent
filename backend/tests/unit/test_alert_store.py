import pytest
from unittest.mock import MagicMock, patch
from schemas.alert import Alert


@pytest.fixture
def store():
    with patch("store.alert_store.get_firestore_client") as mock_client_fn:
        mock_db = MagicMock()
        mock_client_fn.return_value = mock_db
        from store.alert_store import AlertStore

        yield AlertStore(), mock_db


def test_save_creates_new_alert_id(store):
    alert_store, mock_db = store
    mock_doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    alert = Alert(
        watch_id="watch_001",
        user_id="user_001",
        post_id="935227",
        post_url="https://kseattle.com/?uid=935227",
        title="벨뷰 룸 렌트합니다",
        verdict="worth_checking",
        extracted_fields={"location": "Bellevue", "rent": 950},
        summary="A room in Bellevue at $950.",
    )
    result = alert_store.save(alert)

    assert result.alert_id != ""
    mock_doc_ref.set.assert_called_once()


def test_list_by_watch(store):
    alert_store, mock_db = store
    mock_doc = MagicMock()
    mock_doc.to_dict.return_value = {
        "alert_id": "alert_001",
        "watch_id": "watch_001",
        "user_id": "user_001",
        "post_id": "935227",
        "post_url": "https://kseattle.com/?uid=935227",
        "title": "벨뷰 룸 렌트합니다",
        "verdict": "worth_checking",
        "extracted_fields": {"location": "Bellevue", "rent": 950},
        "summary": "A room in Bellevue at $950.",
        "is_read": False,
    }
    mock_db.collection.return_value.where.return_value.order_by.return_value.stream.return_value = [
        mock_doc
    ]

    results = alert_store.list_by_watch("watch_001")

    assert len(results) == 1
    assert results[0].alert_id == "alert_001"
    assert results[0].verdict == "worth_checking"
