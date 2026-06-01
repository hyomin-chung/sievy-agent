import os
from elasticsearch import Elasticsearch


def get_elastic_client() -> Elasticsearch:
    url = os.getenv("ELASTIC_URL", "http://elastic:9200")
    api_key = os.getenv("ELASTIC_API_KEY")

    if api_key:
        return Elasticsearch(hosts=[url], api_key=api_key)
    return Elasticsearch(hosts=[url])


INDEX_NAME = "sievy_posts"

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
    if client.indices.exists(index=INDEX_NAME):
        return
    try:
        client.indices.create(index=INDEX_NAME, mappings=INDEX_MAPPINGS)
    except Exception:
        if not client.indices.exists(index=INDEX_NAME):
            raise
