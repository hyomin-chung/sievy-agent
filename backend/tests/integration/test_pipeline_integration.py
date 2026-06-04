"""
Integration test for scan() and create_watch() pipelines.
Requires real API keys in .env and running Docker stack.

Run integration tests only:
    uv run pytest -m integration -v -s

Skip integration tests (unit only):
    uv run pytest -m "not integration" -v
"""

import pytest
from agents.pipeline import create_watch, scan

KSEATTLE_RENT_URL = "https://www.kseattle.com/벼룩시장/렌트-하숙/"
HOUSING_CRITERIA = {
    "locations": ["Bellevue", "Redmond", "Seattle"],
    "max_rent": 1500,
}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_watch_with_real_kseattle():
    """
    Verifies that create_watch() successfully fetches a baseline
    from the real K-Seattle rent board and saves the Watch to Firestore.
    """
    watch = await create_watch(
        user_id="integration_test_user",
        source_url=KSEATTLE_RENT_URL,
        category="housing",
        criteria=HOUSING_CRITERIA,
    )

    print(f"\nWatch ID: {watch.watch_id}")
    print(f"Source URL: {watch.source_url}")
    print(f"Baseline posts: {len(watch.baseline_post_ids)}")

    assert watch.watch_id != ""
    assert watch.source_url == KSEATTLE_RENT_URL
    assert len(watch.baseline_post_ids) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_scan_with_real_watch():
    """
    Verifies that scan() loads a real Watch from Firestore and runs
    the full pipeline end-to-end without errors.
    ScanOrchestrator (ADK LlmAgent) fetches, indexes, judges posts.
    """
    from store.elastic_store import ElasticStore
    from config import ELASTIC_INDEX_NAME

    watch = await create_watch(
        user_id="integration_test_user",
        source_url=KSEATTLE_RENT_URL,
        category="housing",
        criteria=HOUSING_CRITERIA,
    )

    print(f"\nWatch ID: {watch.watch_id}")

    result = await scan(watch.watch_id)

    print(f"New posts found: {result.new_posts_found}")
    print(f"Alerts created: {result.alerts_created}")
    print(f"Errors: {result.errors}")

    assert result.watch_id == watch.watch_id
    assert result.errors == []

    elastic_store = ElasticStore()
    es_result = elastic_store.client.search(
        index=ELASTIC_INDEX_NAME,
        query={"term": {"watch_id": watch.watch_id}},
    )
    indexed_count = es_result["hits"]["total"]["value"]
    print(f"Elasticsearch indexed posts: {indexed_count}")

    if result.new_posts_found > 0:
        assert indexed_count > 0
