import json
import uuid
from dataclasses import dataclass, field

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from google.genai import types

from config import GEMINI_MODEL, ELASTIC_MCP_URL, ELASTIC_INDEX_NAME
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

        elastic_toolset = MCPToolset(
            connection_params=SseConnectionParams(
                url=ELASTIC_MCP_URL,
            )
        )

        posts_json = json.dumps(
            [{"post_id": p.post_id, "url": p.url, "title": p.title} for p in new_posts],
            ensure_ascii=False,
        )

        agent = Agent(
            name="scan_orchestrator",
            model=GEMINI_MODEL,
            instruction=f"""
You are Sievy's scan orchestrator. Process new posts and create alerts for matching ones.

Watch criteria:
{json.dumps(self.criteria, ensure_ascii=False)}
Category: {self.category}

New posts to process:
{posts_json}

For each post:
1. Call fetch_and_index(post_id, post_url, title) to fetch content and store in Elasticsearch
2. If status is "empty", skip to next post
3. Use the Elasticsearch search tool to search the "{ELASTIC_INDEX_NAME}" index for this post_id
   and read its content (body field)
4. Judge whether the content matches the watch criteria
5. If verdict is "worth_checking" or "needs_checking":
   Call create_alert(post_id, post_url, title, verdict, extracted_fields, summary)
6. If verdict is "ignore", move to next post

Verdict rules:
- worth_checking: clearly matches all key criteria
- needs_checking: partially matches or some criteria unclear
- ignore: does not match

extracted_fields should contain relevant structured data from the post
(e.g. for housing: location, rent, move_in_date, utilities_included)

Process all posts before finishing.
""",
            tools=[
                self.fetch_and_index,
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
            parts=[types.Part(text="Start processing the new posts.")],
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
