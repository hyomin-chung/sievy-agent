import re
import httpx

from connectors.base import PostCandidate
from connectors.firecrawl_connector import FirecrawlConnector
from config import GEMINI_MODEL, GOOGLE_API_KEY


def fetch_body(url: str) -> str:
    connector = FirecrawlConnector()
    post = PostCandidate(post_id="", title="", url=url)
    return connector.fetch_detail(post)


def extract_image_urls(body: str) -> list[str]:
    patterns = [
        r"!\[.*?\]\((https?://[^\)]+)\)",
        r'<img[^>]+src=["\']?(https?://[^\s"\']+)["\']?',
    ]
    urls = []
    for pattern in patterns:
        urls.extend(re.findall(pattern, body))
    return sorted(set(urls))


def extract_attachment_urls(body: str) -> list[str]:
    pattern = r"\[.*?\]\((https?://[^\)]+\.(?:pdf|hwp|docx|zip|pptx))\)"
    return list(set(re.findall(pattern, body, re.IGNORECASE)))


def read_image(image_url: str) -> str:
    try:
        from google import genai
        from google.genai import types

        response = httpx.get(image_url, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "image/jpeg")

        client = genai.Client(api_key=GOOGLE_API_KEY)
        result = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=response.content, mime_type=content_type),
                "Extract all text and information visible in this image. Return plain text only.",
            ],
        )
        return result.text or ""
    except Exception:
        return ""


def fetch_attachment(url: str) -> str:
    try:
        from google import genai
        from google.genai import types

        response = httpx.get(url, timeout=15)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "application/pdf")

        client = genai.Client(api_key=GOOGLE_API_KEY)
        result = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=response.content, mime_type=content_type),
                "Extract all text and information from this document. Return plain text only.",
            ],
        )
        return result.text or ""
    except Exception:
        return ""


def fetch_post_content(post: PostCandidate) -> str:
    parts = []

    body = fetch_body(post.url)
    if body:
        parts.append(body)

    for image_url in extract_image_urls(body):
        text = read_image(image_url)
        if text:
            parts.append(text)

    for attachment_url in extract_attachment_urls(body):
        text = fetch_attachment(attachment_url)
        if text:
            parts.append(text)

    return "\n".join(parts)
