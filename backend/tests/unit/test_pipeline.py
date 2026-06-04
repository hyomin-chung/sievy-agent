import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from schemas.watch import Watch
from connectors.base import PostCandidate


@pytest.fixture
def mock_watch():
    return Watch(
        watch_id="watch_001",
        user_id="user_001",
        source_url="https://kseattle.com/rentlodge/",
        category="housing",
        criteria={"locations": ["Bellevue"], "max_rent": 1000},
        baseline_post_ids=["935227"],
    )


@pytest.fixture
def mock_new_post():
    return PostCandidate(
        post_id="935228",
        title="벨뷰 룸 렌트합니다",
        url="https://kseattle.com/?uid=935228",
    )


@pytest.mark.asyncio
async def test_create_watch(mock_watch):
    with (
        patch("agents.pipeline.FirecrawlConnector") as mock_connector_class,
        patch("agents.pipeline.FeedDetector") as mock_detector_class,
        patch("agents.pipeline.WatchStore") as mock_watch_store_class,
    ):
        mock_connector_class.return_value = MagicMock()
        mock_detector = MagicMock()
        mock_detector.create_baseline.return_value = {"935227", "935228"}
        mock_detector_class.return_value = mock_detector

        mock_watch_store = MagicMock()
        mock_watch_store.save.return_value = mock_watch
        mock_watch_store_class.return_value = mock_watch_store

        from agents.pipeline import create_watch

        result = await create_watch(
            user_id="user_001",
            source_url="https://kseattle.com/rentlodge/",
            category="housing",
            criteria={"locations": ["Bellevue"], "max_rent": 1000},
        )

        mock_detector.create_baseline.assert_called_once()
        mock_watch_store.save.assert_called_once()
        assert result.watch_id == "watch_001"


@pytest.mark.asyncio
async def test_scan_calls_orchestrator(mock_watch, mock_new_post):
    with (
        patch("agents.pipeline.WatchStore") as mock_watch_store_class,
        patch("agents.pipeline.FeedDetector") as mock_detector_class,
        patch("agents.pipeline.FirecrawlConnector") as mock_connector_class,
        patch("agents.pipeline.ScanOrchestrator") as mock_orchestrator_class,
    ):
        mock_watch_store = MagicMock()
        mock_watch_store.get.return_value = mock_watch
        mock_watch_store_class.return_value = mock_watch_store

        mock_detector = MagicMock()
        mock_detector.detect_new_posts.return_value = [mock_new_post]
        mock_detector_class.return_value = mock_detector

        mock_connector_class.return_value = MagicMock()

        from agents.scan_orchestrator import ScanResult

        mock_orchestrator = MagicMock()
        mock_orchestrator.run = AsyncMock(
            return_value=ScanResult(
                watch_id="watch_001",
                source_url="https://kseattle.com/rentlodge/",
                new_posts_found=1,
                alerts_created=1,
            )
        )
        mock_orchestrator_class.return_value = mock_orchestrator

        from agents.pipeline import scan

        result = await scan("watch_001")

        mock_orchestrator.run.assert_called_once()
        assert result.new_posts_found == 1
        assert result.alerts_created == 1


@pytest.mark.asyncio
async def test_scan_raises_when_watch_not_found():
    with (
        patch("agents.pipeline.WatchStore") as mock_watch_store_class,
        patch("agents.pipeline.FeedDetector"),
        patch("agents.pipeline.FirecrawlConnector"),
        patch("agents.pipeline.ScanOrchestrator"),
    ):
        mock_watch_store = MagicMock()
        mock_watch_store.get.return_value = None
        mock_watch_store_class.return_value = mock_watch_store

        from agents.pipeline import scan

        with pytest.raises(ValueError):
            await scan("nonexistent_watch")
