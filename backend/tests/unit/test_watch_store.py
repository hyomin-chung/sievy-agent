import pytest
from unittest.mock import MagicMock, patch
from schemas.watch import Watch


@pytest.fixture
def store():
    with patch("store.watch_store.get_firestore_client") as mock_client_fn:
        mock_db = MagicMock()
        mock_client_fn.return_value = mock_db
        from store.watch_store import WatchStore

        yield WatchStore(), mock_db


def test_save_creates_new_watch_id(store):
    watch_store, mock_db = store
    mock_doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    watch = Watch(
        user_id="user_001",
        source_url="https://kseattle.com/rentlodge/",
        category="housing",
        criteria={"locations": ["Bellevue"], "max_rent": 1000},
    )
    result = watch_store.save(watch)

    assert result.watch_id != ""
    mock_doc_ref.set.assert_called_once()


def test_get_returns_watch(store):
    watch_store, mock_db = store
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "watch_id": "watch_001",
        "user_id": "user_001",
        "source_url": "https://kseattle.com/rentlodge/",
        "category": "housing",
        "criteria": {"locations": ["Bellevue"], "max_rent": 1000},
        "baseline_post_ids": ["935227"],
    }
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    result = watch_store.get("watch_001")

    assert result.watch_id == "watch_001"
    assert result.user_id == "user_001"


def test_get_returns_none_when_not_found(store):
    watch_store, mock_db = store
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    result = watch_store.get("nonexistent")

    assert result is None


def test_update_baseline(store):
    watch_store, mock_db = store
    mock_doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    watch_store.update_baseline("watch_001", ["935227", "935228"])

    mock_doc_ref.update.assert_called_once()
    call_args = mock_doc_ref.update.call_args[0][0]
    assert call_args["baseline_post_ids"] == ["935227", "935228"]
