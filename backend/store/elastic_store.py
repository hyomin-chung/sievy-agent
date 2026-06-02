import hashlib
from datetime import datetime, timezone

from config import ELASTIC_INDEX_NAME
from connectors.base import PostCandidate
from judge.judge_agent import JudgeResult
from store.elastic_client import ensure_index, get_elastic_client


class ElasticStore:
    def __init__(self):
        self.client = get_elastic_client()
        ensure_index(self.client)

    def index_post(
        self,
        watch_id: str,
        post: PostCandidate,
        body: str,
        category: str,
        judge_result: JudgeResult,
    ) -> None:
        doc = {
            "post_id": post.post_id,
            "watch_id": watch_id,
            "source_url": post.url,
            "title": post.title,
            "body": body,
            "category": category,
            "extracted": judge_result.extracted_fields,
            "verdict": judge_result.verdict,
            "crawled_at": datetime.now(tz=timezone.utc).isoformat(),
        }

        self.client.index(
            index=ELASTIC_INDEX_NAME,
            id=self._make_doc_id(watch_id, post.post_id),
            document=doc,
        )

    def _make_doc_id(self, watch_id: str, post_id: str) -> str:
        raw = f"{watch_id}:{post_id}"
        return hashlib.sha256(raw.encode()).hexdigest()
