import asyncio
import re
import httpx
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from config import GEMINI_MODEL
from connectors.base import PostCandidate
from connectors.firecrawl_connector import FirecrawlConnector


def fetch_body(url: str) -> dict:
    """Fetch the main content of a post URL as markdown text.

    Args:
        url: The URL of the post to fetch.

    Returns:
        dict with 'body' key containing markdown text, or 'error' if failed.
    """
    try:
        connector = FirecrawlConnector()
        post = PostCandidate(post_id="", title="", url=url)
        body = connector.fetch_detail(post)
        return {"body": body}
    except Exception as e:
        return {"error": str(e), "body": ""}


def fetch_images(body: str) -> dict:
    """Extract image URLs from markdown body text.

    Args:
        body: Markdown text that may contain image links.

    Returns:
        dict with 'image_urls' key containing list of image URLs found.
    """
    patterns = [
        r"!\[.*?\]\((https?://[^\)]+)\)",
        r'<img[^>]+src=["\']?(https?://[^\s"\']+)["\']?',
    ]
    urls = []
    for pattern in patterns:
        urls.extend(re.findall(pattern, body))
    return {"image_urls": list(set(urls))}


def read_image(image_url: str) -> dict:
    """Read and extract text content from an image using Gemini multimodal.

    Args:
        image_url: URL of the image to read and extract text from.

    Returns:
        dict with 'content' key containing extracted text from the image.
    """
    try:
        from google import genai
        from config import GOOGLE_API_KEY

        response = httpx.get(image_url, timeout=10)
        response.raise_for_status()
        image_data = response.content
        content_type = response.headers.get("content-type", "image/jpeg")

        client = genai.Client(api_key=GOOGLE_API_KEY)
        result = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=image_data, mime_type=content_type),
                "Extract all text and information visible in this image. Return plain text only.",
            ],
        )
        return {"content": result.text}
    except Exception as e:
        return {"content": "", "error": str(e)}


def fetch_attachment(url: str) -> dict:
    """Fetch and read content from an attachment such as PDF or document file.

    Args:
        url: URL of the attachment to fetch and extract text from.

    Returns:
        dict with 'content' key containing extracted text from the attachment.
    """
    try:
        from google import genai
        from config import GOOGLE_API_KEY

        response = httpx.get(url, timeout=15)
        response.raise_for_status()
        file_data = response.content
        content_type = response.headers.get("content-type", "application/pdf")

        client = genai.Client(api_key=GOOGLE_API_KEY)
        result = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=file_data, mime_type=content_type),
                "Extract all text and information from this document. Return plain text only.",
            ],
        )
        return {"content": result.text}
    except Exception as e:
        return {"content": "", "error": str(e)}


APP_NAME = "sievy"
USER_ID = "system"

detail_fetch_agent = Agent(
    name="detail_fetch_agent",
    model=GEMINI_MODEL,
    instruction="""
    You are a post content fetcher for Sievy, a source-bound alert filter.
    Given a post URL, your job is to collect ALL available content from the post.

    Follow these steps:
    1. Always call fetch_body first to get the main content as markdown
    2. If the body contains image links (![...](...) patterns or <img> tags),
       call fetch_images to extract the URLs, then call read_image for each image URL
    3. If the body contains attachment links (PDF, zip, hwp, docx, etc.),
       call fetch_attachment for each attachment URL
    4. Combine all collected text into a single unified response

    Return ALL collected content as plain text. Do not summarize or filter anything.
    Include all text from the body, images, and attachments.
    """,
    tools=[fetch_body, fetch_images, read_image, fetch_attachment],
)


class DetailFetchAgent:
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=detail_fetch_agent,
            app_name=APP_NAME,
            session_service=self.session_service,
        )

    async def run_async(self, post: PostCandidate) -> str:
        session = await self.session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=f"session_{post.post_id}",
        )

        message = types.Content(
            role="user",
            parts=[types.Part(text=f"Fetch content from: {post.url}")],
        )

        result = ""
        async for event in self.runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        result += part.text

        return result

    def run(self, post: PostCandidate) -> str:
        return asyncio.run(self.run_async(post))
