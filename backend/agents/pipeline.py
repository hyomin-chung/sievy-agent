from connectors.firecrawl_connector import FirecrawlConnector
from feed.feed_detector import FeedDetector
from store.watch_store import WatchStore
from schemas.watch import Watch
from agents.scan_orchestrator import ScanOrchestrator, ScanResult


def _get_connector(source_url: str):
    return FirecrawlConnector()


async def create_watch(
    user_id: str,
    source_url: str,
    category: str,
    criteria: dict,
    note: str = "",
) -> Watch:
    connector = _get_connector(source_url)
    feed_detector = FeedDetector()
    watch_store = WatchStore()

    post_url_pattern = {}
    if isinstance(connector, FirecrawlConnector):
        try:
            post_url_pattern = connector.detect_post_url_pattern(source_url)
        except Exception:
            post_url_pattern = {}

    baseline_post_ids = list(
        feed_detector.create_baseline(
            connector, source_url, url_pattern=post_url_pattern
        )
    )

    watch = Watch(
        user_id=user_id,
        source_url=source_url,
        category=category,
        criteria=criteria,
        baseline_post_ids=baseline_post_ids,
        post_url_pattern=post_url_pattern,
        note=note,
    )
    return watch_store.save(watch)


async def scan(watch_id: str) -> ScanResult:
    watch_store = WatchStore()
    watch = watch_store.get(watch_id)
    if not watch:
        raise ValueError(f"Watch not found: {watch_id}")

    connector = _get_connector(watch.source_url)
    feed_detector = FeedDetector()
    baseline_post_ids = set(watch.baseline_post_ids)

    new_posts = feed_detector.detect_new_posts(
        connector,
        watch.source_url,
        baseline_post_ids,
        url_pattern=watch.post_url_pattern,
    )

    orchestrator = ScanOrchestrator(
        watch_id=watch_id,
        user_id=watch.user_id,
        source_url=watch.source_url,
        category=watch.category,
        criteria=watch.criteria,
    )

    result = await orchestrator.run(new_posts)

    if not result.errors:
        current_ids = list(baseline_post_ids) + [p.post_id for p in new_posts]
        watch_store.update_baseline(watch_id, current_ids)

    return result
