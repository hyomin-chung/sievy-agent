from elasticsearch import Elasticsearch
from config import ELASTIC_URL, ELASTIC_API_KEY, ELASTIC_INDEX_NAME


def get_elastic_client() -> Elasticsearch:
    if ELASTIC_API_KEY:
        return Elasticsearch(hosts=[ELASTIC_URL], api_key=ELASTIC_API_KEY)
    return Elasticsearch(hosts=[ELASTIC_URL])


INDEX_MAPPINGS = {
    "properties": {
        "post_id": {"type": "keyword"},
        "watch_id": {"type": "keyword"},
        "source_url": {"type": "keyword"},
        "title": {"type": "text", "analyzer": "standard"},
        "body": {"type": "text", "analyzer": "standard"},
        "category": {"type": "keyword"},
        "extracted": {"type": "object", "dynamic": True},
        "verdict": {"type": "keyword"},
        "crawled_at": {"type": "date"},
    }
}


def ensure_index(client: Elasticsearch) -> None:
    if client.indices.exists(index=ELASTIC_INDEX_NAME):
        return
    try:
        client.indices.create(index=ELASTIC_INDEX_NAME, mappings=INDEX_MAPPINGS)
    except Exception:
        if not client.indices.exists(index=ELASTIC_INDEX_NAME):
            raise
