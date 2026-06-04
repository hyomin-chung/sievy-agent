import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from api.main import app

client = TestClient(app)


@pytest.fixture
def mock_watch():
    from schemas.watch import Watch

    return Watch(
        watch_id="watch_001",
        user_id="user_001",
        source_url="https://kseattle.com/rentlodge/",
        category="housing",
        criteria={"locations": ["Bellevue"], "max_rent": 1000},
        baseline_post_ids=["935227"],
    )


@pytest.fixture
def mock_alert():
    from schemas.alert import Alert
    from datetime import datetime, timezone

    return Alert(
        alert_id="alert_001",
        watch_id="watch_001",
        user_id="user_001",
        post_id="935228",
        post_url="https://kseattle.com/?uid=935228",
        title="벨뷰 룸 렌트합니다",
        verdict="worth_checking",
        extracted_fields={"location": "Bellevue", "rent": 950},
        summary="A room in Bellevue at $950.",
        created_at=datetime.now(timezone.utc),
    )


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_watch(mock_watch):
    with patch(
        "api.routes.watches.create_watch", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = mock_watch
        response = client.post(
            "/watches",
            json={
                "source_url": "https://kseattle.com/rentlodge/",
                "category": "housing",
                "criteria": {"locations": ["Bellevue"], "max_rent": 1000},
            },
            headers={"x-user-id": "user_001"},
        )
    assert response.status_code == 201
    assert response.json()["watch_id"] == "watch_001"


def test_create_watch_missing_user_id():
    response = client.post(
        "/watches",
        json={
            "source_url": "https://kseattle.com/rentlodge/",
            "category": "housing",
            "criteria": {},
        },
    )
    assert response.status_code == 422


def test_get_watch(mock_watch):
    with patch("api.routes.watches.WatchStore") as mock_store_class:
        mock_store = MagicMock()
        mock_store.get.return_value = mock_watch
        mock_store_class.return_value = mock_store
        response = client.get(
            "/watches/watch_001",
            headers={"x-user-id": "user_001"},
        )
    assert response.status_code == 200
    assert response.json()["watch_id"] == "watch_001"


def test_get_watch_not_found():
    with patch("api.routes.watches.WatchStore") as mock_store_class:
        mock_store = MagicMock()
        mock_store.get.return_value = None
        mock_store_class.return_value = mock_store
        response = client.get(
            "/watches/nonexistent",
            headers={"x-user-id": "user_001"},
        )
    assert response.status_code == 404


def test_scan_endpoint(mock_watch):
    with (
        patch("api.routes.watches.WatchStore") as mock_store_class,
        patch("agents.pipeline.WatchStore") as mock_pipeline_store_class,
        patch("agents.pipeline.FeedDetector") as mock_detector_class,
        patch("agents.pipeline.ScanOrchestrator") as mock_orchestrator_class,
        patch("agents.pipeline.FirecrawlConnector"),
    ):
        mock_store = MagicMock()
        mock_store.get.return_value = mock_watch
        mock_store_class.return_value = mock_store

        mock_pipeline_store = MagicMock()
        mock_pipeline_store.get.return_value = mock_watch
        mock_pipeline_store_class.return_value = mock_pipeline_store

        mock_detector = MagicMock()
        mock_detector.detect_new_posts.return_value = []
        mock_detector_class.return_value = mock_detector

        from agents.scan_orchestrator import ScanResult

        mock_orchestrator = MagicMock()
        mock_orchestrator.run = AsyncMock(
            return_value=ScanResult(
                watch_id="watch_001",
                source_url="https://kseattle.com/rentlodge/",
            )
        )
        mock_orchestrator_class.return_value = mock_orchestrator

        response = client.post(
            "/watches/watch_001/scan",
            headers={"x-user-id": "user_001"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "scan started"


def test_list_alerts(mock_alert):
    with patch("api.routes.alerts.AlertStore") as mock_store_class:
        mock_store = MagicMock()
        mock_store.list_by_user.return_value = [mock_alert]
        mock_store_class.return_value = mock_store
        response = client.get(
            "/alerts",
            headers={"x-user-id": "user_001"},
        )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["alert_id"] == "alert_001"


def test_mark_alert_read(mock_alert):
    with patch("api.routes.alerts.AlertStore") as mock_store_class:
        mock_store = MagicMock()
        mock_store.list_by_user.return_value = [mock_alert]
        mock_store_class.return_value = mock_store
        response = client.patch(
            "/alerts/alert_001/read",
            headers={"x-user-id": "user_001"},
        )
    assert response.status_code == 204
