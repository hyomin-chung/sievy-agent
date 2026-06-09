from elasticsearch import Elasticsearch
from config import ELASTIC_URL, ELASTIC_API_KEY, ELASTIC_INDEX_NAME


def get_elastic_client() -> Elasticsearch:
    if ELASTIC_API_KEY:
        return Elasticsearch(
            hosts=[ELASTIC_URL],
            api_key=ELASTIC_API_KEY,
            http_compress=True,
        )
    return Elasticsearch(
        hosts=[ELASTIC_URL],
        http_compress=True,
    )


INDEX_MAPPINGS = {
    "properties": {
        "watch_id": {"type": "keyword"},
        "post_id": {"type": "keyword"},
        "post_url": {"type": "keyword"},
        "body": {"type": "semantic_text"},
        "category": {"type": "keyword"},
        "crawled_at": {"type": "date"},
    }
}


def ensure_index(client: Elasticsearch) -> None:
    if client.indices.exists(index=ELASTIC_INDEX_NAME):
        return
    try:
        client.indices.create(
            index=ELASTIC_INDEX_NAME,
            mappings=INDEX_MAPPINGS,
        )
    except Exception:
        if not client.indices.exists(index=ELASTIC_INDEX_NAME):
            raise
