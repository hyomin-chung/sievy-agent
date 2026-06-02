import pytest
from unittest.mock import MagicMock, patch, AsyncMock


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
def mock_new_post():
    from connectors.base import PostCandidate

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
        mock_connector = MagicMock()
        mock_connector_class.return_value = mock_connector

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
async def test_scan_creates_alert_for_worth_checking(mock_watch, mock_new_post):
    with (
        patch("agents.pipeline.WatchStore") as mock_watch_store_class,
        patch("agents.pipeline.AlertStore") as mock_alert_store_class,
        patch("agents.pipeline.ElasticStore") as mock_elastic_class,
        patch("agents.pipeline.FeedDetector") as mock_detector_class,
        patch("agents.pipeline.JudgeAgent") as mock_judge_class,
        patch("agents.pipeline.DetailFetchAgent") as mock_fetch_class,
        patch("agents.pipeline.FirecrawlConnector") as mock_connector_class,
    ):
        mock_watch_store = MagicMock()
        mock_watch_store.get.return_value = mock_watch
        mock_watch_store_class.return_value = mock_watch_store

        mock_alert_store = MagicMock()
        mock_alert_store_class.return_value = mock_alert_store

        mock_elastic = MagicMock()
        mock_elastic_class.return_value = mock_elastic

        mock_detector = MagicMock()
        mock_detector.detect_new_posts.return_value = [mock_new_post]
        mock_detector_class.return_value = mock_detector

        from judge.judge_agent import JudgeResult

        mock_judge = MagicMock()
        mock_judge.judge.return_value = JudgeResult(
            verdict="worth_checking",
            extracted_fields={"location": "Bellevue", "rent": 950},
            verdict_reason="Location and rent match.",
            summary="A room in Bellevue at $950.",
        )
        mock_judge_class.return_value = mock_judge

        mock_fetch = MagicMock()
        mock_fetch.run_async = AsyncMock(return_value="벨뷰 룸 렌트합니다. 월 $950.")
        mock_fetch_class.return_value = mock_fetch

        mock_connector_class.return_value = MagicMock()

        from agents.pipeline import scan

        result = await scan("watch_001")

        assert result.new_posts_found == 1
        assert result.alerts_created == 1
        mock_alert_store.save.assert_called_once()
        mock_elastic.index_post.assert_called_once()


@pytest.mark.asyncio
async def test_scan_skips_alert_for_ignore(mock_watch, mock_new_post):
    with (
        patch("agents.pipeline.WatchStore") as mock_watch_store_class,
        patch("agents.pipeline.AlertStore") as mock_alert_store_class,
        patch("agents.pipeline.ElasticStore") as mock_elastic_class,
        patch("agents.pipeline.FeedDetector") as mock_detector_class,
        patch("agents.pipeline.JudgeAgent") as mock_judge_class,
        patch("agents.pipeline.DetailFetchAgent") as mock_fetch_class,
        patch("agents.pipeline.FirecrawlConnector") as mock_connector_class,
    ):
        mock_watch_store = MagicMock()
        mock_watch_store.get.return_value = mock_watch
        mock_watch_store_class.return_value = mock_watch_store

        mock_alert_store = MagicMock()
        mock_alert_store_class.return_value = mock_alert_store

        mock_elastic_class.return_value = MagicMock()
        mock_detector = MagicMock()
        mock_detector.detect_new_posts.return_value = [mock_new_post]
        mock_detector_class.return_value = mock_detector

        from judge.judge_agent import JudgeResult

        mock_judge = MagicMock()
        mock_judge.judge.return_value = JudgeResult(
            verdict="ignore",
            extracted_fields={},
            verdict_reason="Does not match criteria.",
            summary="A room outside criteria.",
        )
        mock_judge_class.return_value = mock_judge

        mock_fetch = MagicMock()
        mock_fetch.run_async = AsyncMock(return_value="시애틀 룸 렌트합니다. 월 $2000.")
        mock_fetch_class.return_value = mock_fetch

        mock_connector_class.return_value = MagicMock()

        from agents.pipeline import scan

        result = await scan("watch_001")

        assert result.alerts_created == 0
        mock_alert_store.save.assert_not_called()


@pytest.mark.asyncio
async def test_scan_raises_when_watch_not_found():
    with (
        patch("agents.pipeline.WatchStore") as mock_watch_store_class,
        patch("agents.pipeline.AlertStore"),
        patch("agents.pipeline.ElasticStore"),
        patch("agents.pipeline.FeedDetector"),
        patch("agents.pipeline.JudgeAgent"),
        patch("agents.pipeline.DetailFetchAgent"),
        patch("agents.pipeline.FirecrawlConnector"),
    ):
        mock_watch_store = MagicMock()
        mock_watch_store.get.return_value = None
        mock_watch_store_class.return_value = mock_watch_store

        from agents.pipeline import scan

        with pytest.raises(ValueError):
            await scan("nonexistent_watch")
