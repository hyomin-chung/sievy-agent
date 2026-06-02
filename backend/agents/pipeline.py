from dataclasses import dataclass, field

from connectors.firecrawl_connector import FirecrawlConnector
from connectors.reddit import RedditConnector
from feed.feed_detector import FeedDetector
from judge.judge_agent import JudgeAgent
from store.elastic_store import ElasticStore
from store.watch_store import WatchStore
from store.alert_store import AlertStore
from agents.detail_fetch_agent import DetailFetchAgent
from schemas.watch import Watch
from schemas.alert import Alert


@dataclass
class ScanResult:
    watch_id: str
    source_url: str
    new_posts_found: int = 0
    alerts_created: int = 0
    errors: list[str] = field(default_factory=list)


def _get_connector(source_url: str):
    if "reddit.com" in source_url:
        return RedditConnector()
    return FirecrawlConnector()


async def create_watch(
    user_id: str,
    source_url: str,
    category: str,
    criteria: dict,
) -> Watch:
    connector = _get_connector(source_url)
    feed_detector = FeedDetector()
    watch_store = WatchStore()

    baseline_post_ids = list(feed_detector.create_baseline(connector, source_url))

    watch = Watch(
        user_id=user_id,
        source_url=source_url,
        category=category,
        criteria=criteria,
        baseline_post_ids=baseline_post_ids,
    )
    return watch_store.save(watch)


async def scan(watch_id: str) -> ScanResult:
    watch_store = WatchStore()
    alert_store = AlertStore()
    elastic_store = ElasticStore()
    feed_detector = FeedDetector()
    judge_agent = JudgeAgent()
    detail_fetch_agent = DetailFetchAgent()

    watch = watch_store.get(watch_id)
    if not watch:
        raise ValueError(f"Watch not found: {watch_id}")

    connector = _get_connector(watch.source_url)
    baseline_post_ids = set(watch.baseline_post_ids)

    new_posts = feed_detector.detect_new_posts(
        connector, watch.source_url, baseline_post_ids
    )

    result = ScanResult(
        watch_id=watch_id,
        source_url=watch.source_url,
        new_posts_found=len(new_posts),
    )

    current_post_ids = list(baseline_post_ids)

    for post in new_posts:
        try:
            post_content = await detail_fetch_agent.run_async(post)

            if not post_content.strip():
                continue

            judge_result = judge_agent.judge(
                body=post_content,
                category=watch.category,
                criteria=watch.criteria,
            )

            elastic_store.index_post(
                watch_id=watch_id,
                post=post,
                body=post_content,
                category=watch.category,
                judge_result=judge_result,
            )

            if judge_result.verdict != "ignore":
                alert = Alert(
                    watch_id=watch_id,
                    user_id=watch.user_id,
                    post_id=post.post_id,
                    post_url=post.url,
                    title=post.title,
                    verdict=judge_result.verdict,
                    extracted_fields=judge_result.extracted_fields,
                    summary=judge_result.summary,
                )
                alert_store.save(alert)
                result.alerts_created += 1

            current_post_ids.append(post.post_id)

        except Exception as e:
            result.errors.append(f"{post.post_id}: {str(e)}")

    watch_store.update_baseline(watch_id, current_post_ids)

    return result
