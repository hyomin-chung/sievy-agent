from datetime import datetime, timezone

from config import ELASTIC_INDEX_NAME
from connectors.base import PostCandidate
from store.elastic_client import ensure_index, get_elastic_client


class ElasticStore:
    def __init__(self):
        self.client = get_elastic_client()
        ensure_index(self.client)

    def index_post_content(
        self,
        watch_id: str,
        post: PostCandidate,
        body: str,
        category: str,
    ) -> None:
        doc = {
            "post_id": post.post_id,
            "watch_id": watch_id,
            "post_url": post.url,
            "title": post.title or "",
            "body": body,
            "category": category,
            "crawled_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        self.client.index(
            index=ELASTIC_INDEX_NAME,
            id=f"{watch_id}_{post.post_id}",
            document=doc,
        )

    def search_by_watch(self, watch_id: str, size: int = 20) -> list[dict]:
        result = self.client.search(
            index=ELASTIC_INDEX_NAME,
            query={"term": {"watch_id": watch_id}},
            sort=[{"crawled_at": {"order": "desc"}}],
            size=size,
        )
        return [hit["_source"] for hit in result["hits"]["hits"]]

    def delete_by_watch(self, watch_id: str) -> None:
        self.client.delete_by_query(
            index=ELASTIC_INDEX_NAME,
            body={"query": {"term": {"watch_id": watch_id}}},
            ignore_unavailable=True,
        )
