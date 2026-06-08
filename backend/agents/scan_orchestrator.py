import json
import uuid
from dataclasses import dataclass, field
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StreamableHTTPConnectionParams,
)
from google.genai import types

from config import (
    ELASTIC_MCP_API_KEY,
    GEMINI_MODEL,
    ELASTIC_MCP_URL,
    ELASTIC_INDEX_NAME,
)
from connectors.base import PostCandidate
from feed.detail_fetcher import fetch_post_content
from store.elastic_store import ElasticStore
from store.alert_store import AlertStore
from schemas.alert import Alert


@dataclass
class ScanResult:
    watch_id: str
    source_url: str
    new_posts_found: int = 0
    alerts_created: int = 0
    errors: list[str] = field(default_factory=list)


APP_NAME = "sievy"
USER_ID = "system"


class ScanOrchestrator:
    def __init__(
        self,
        watch_id: str,
        user_id: str,
        source_url: str,
        category: str,
        criteria: dict,
    ):
        self.watch_id = watch_id
        self.user_id = user_id
        self.source_url = source_url
        self.category = category
        self.criteria = criteria

        self.elastic_store = ElasticStore()
        self.alert_store = AlertStore()
        self.result = ScanResult(
            watch_id=watch_id,
            source_url=source_url,
        )

    def fetch_and_index(self, post_id: str, post_url: str, title: str) -> dict:
        """Fetch post content including body, images, attachments and index to Elasticsearch.

        Args:
            post_id: Unique ID of the post
            post_url: URL of the post to fetch
            title: Title of the post

        Returns:
            dict with post_id and status (indexed or empty)
        """
        post = PostCandidate(post_id=post_id, title=title, url=post_url)
        content = fetch_post_content(post)

        if not content.strip():
            return {"post_id": post_id, "status": "empty"}

        self.elastic_store.index_post_content(
            watch_id=self.watch_id,
            post=post,
            body=content,
            category=self.category,
        )
        return {"post_id": post_id, "status": "indexed"}

    def create_alert(
        self,
        post_id: str,
        post_url: str,
        title: str,
        verdict: str,
        extracted_fields: dict,
        summary: str,
    ) -> dict:
        """Save alert to Firestore when a post matches the watch criteria.

        Args:
            post_id: Unique ID of the post
            post_url: URL of the post
            title: Title of the post
            verdict: worth_checking or needs_checking
            extracted_fields: Structured fields extracted from the post
            summary: One sentence summary of the post

        Returns:
            dict with alert_id and status
        """
        alert = Alert(
            watch_id=self.watch_id,
            user_id=self.user_id,
            post_id=post_id,
            post_url=post_url,
            title=title or summary,
            verdict=verdict,
            extracted_fields=extracted_fields,
            summary=summary,
        )
        saved = self.alert_store.save(alert)
        self.result.alerts_created += 1
        return {"alert_id": saved.alert_id, "status": "saved"}

    async def run(self, new_posts: list[PostCandidate]) -> ScanResult:
        self.result.new_posts_found = len(new_posts)

        if not new_posts:
            return self.result

        async def fetch_one(post: PostCandidate, retries: int = 2):
            for attempt in range(retries + 1):
                try:
                    return await asyncio.to_thread(
                        self.fetch_and_index, post.post_id, post.url, post.title
                    )
                except Exception as e:
                    if attempt == retries:
                        self.result.errors.append(f"{post.post_id}: {str(e)[:100]}")
                        return {"post_id": post.post_id, "status": "error"}
                    await asyncio.sleep(2)

        results = await asyncio.gather(*[fetch_one(p) for p in new_posts])
        indexed = [
            p for p, r in zip(new_posts, results) if r.get("status") == "indexed"
        ]

        if not indexed:
            return self.result

        elastic_toolset = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=ELASTIC_MCP_URL,
                headers={"Authorization": f"ApiKey {ELASTIC_MCP_API_KEY}"}
                if ELASTIC_MCP_API_KEY
                else {},
            )
        )

        criteria_keywords = " ".join(str(v) for v in self.criteria.values() if v)
        indexed_post_ids = [p.post_id for p in indexed]

        agent = Agent(
            name="scan_orchestrator",
            model=GEMINI_MODEL,
            instruction=f"""
You are Sievy's scan orchestrator.
{len(indexed)} posts have been indexed into Elasticsearch index "{ELASTIC_INDEX_NAME}".

Watch criteria:
{json.dumps(self.criteria, ensure_ascii=False)}

STEP 1: Call the Elasticsearch "search" tool ONCE with these parameters:
- index_pattern: "{ELASTIC_INDEX_NAME}"
- query:
{{
  "query": {{
    "bool": {{
      "filter": [
        {{"term": {{"watch_id": "{self.watch_id}"}}}},
        {{"terms": {{"post_id": {json.dumps(indexed_post_ids)}}}}}
      ],
      "should": [{{"semantic": {{"field": "body", "query": "{criteria_keywords}"}}}}],
      "minimum_should_match": 1
    }}
  }},
  "size": 20,
  "_source": ["post_id", "post_url", "body", "title"]
}}

Do NOT modify watch_id or index_pattern.
Do NOT call the search tool more than once.

STEP 2: For each document returned from STEP 1:
Read the "body" field and judge it against the watch criteria above.
- worth_checking: ALL key criteria clearly present and matching in the content
- needs_checking: related to the criteria but some information is missing or unclear
- ignore: completely unrelated to the criteria

STEP 3: For worth_checking and needs_checking ONLY:
Call create_alert(post_id, post_url, title, verdict, extracted_fields, summary)
- extracted_fields: ONLY include criteria-relevant fields found in the body.
  Do NOT include post_id, post_url, watch_id, or any internal metadata.
  Example for housing: {{"location": "Federal Way", "rent": "$850/month", "utilities": "included"}}

Do NOT call fetch_and_index. It is already done.
Do NOT call the search tool again after STEP 1.
""",
            tools=[
                self.create_alert,
                elastic_toolset,
            ],
        )

        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=f"scan_{self.watch_id}_{uuid.uuid4().hex[:8]}",
        )

        runner = Runner(
            agent=agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        message = types.Content(
            role="user",
            parts=[types.Part(text="Start processing.")],
        )

        try:
            async for event in runner.run_async(
                user_id=USER_ID,
                session_id=session.id,
                new_message=message,
            ):
                pass
        except Exception as e:
            self.result.errors.append(str(e))
        finally:
            await elastic_toolset.close()

        return self.result
