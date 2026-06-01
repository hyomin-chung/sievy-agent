import json
from dataclasses import dataclass, field
from config import config
from google import genai


HOUSING_PROMPT = """You are a housing post analyzer for Sievy, an AI alert filter.
Extract structured fields from the following Korean/English rental post and determine if it matches the watch criteria.

Watch criteria:
{criteria}

Return ONLY valid JSON with this exact schema:
{{
  "location": "city/area name or null",
  "rent": number or null,
  "utilities_included": true or false or null,
  "move_in_date": "date string or description or null",
  "duration": "short_term or long_term or null",
  "transit_access": "good or limited or null",
  "gender_preference": "male or female or any or null",
  "confidence": "high or medium or low",
  "summary": "one sentence in English",
  "verdict": "worth_checking or needs_checking or ignore",
  "verdict_reason": "brief reason why"
}}

Post body:
{body}"""

OPPORTUNITY_PROMPT = """You are an opportunity post analyzer for Sievy, an AI alert filter.
Extract structured fields from the following post and determine if it matches the watch criteria.

Watch criteria:
{criteria}

Return ONLY valid JSON with this exact schema:
{{
  "deadline": "date string or null",
  "eligibility": "description or null",
  "funding_amount": number or null,
  "location": "online or in-person or hybrid or null",
  "organizer": "string or null",
  "open_to_international": true or false or null,
  "confidence": "high or medium or low",
  "summary": "one sentence in English",
  "verdict": "worth_checking or needs_checking or ignore",
  "verdict_reason": "brief reason why"
}}

Post body:
{body}"""

PROMPTS = {
    "housing": HOUSING_PROMPT,
    "opportunity": OPPORTUNITY_PROMPT,
}


@dataclass
class JudgeResult:
    verdict: str
    extracted_fields: dict
    verdict_reason: str
    summary: str
    confidence: str = "medium"
    raw: dict = field(default_factory=dict)


class JudgeAgent:
    def __init__(self, api_key: str | None = None):
        self.client = genai.Client(api_key=api_key or config.GOOGLE_API_KEY)

    def judge(self, body: str, category: str, criteria: dict) -> JudgeResult:
        prompt_template = PROMPTS.get(category, HOUSING_PROMPT)
        prompt = prompt_template.format(
            criteria=json.dumps(criteria, ensure_ascii=False),
            body=body,
        )

        response = self.client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
        )

        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])

        data = json.loads(text)

        verdict = data.get("verdict", "needs_checking")
        if verdict not in ("worth_checking", "needs_checking", "ignore"):
            verdict = "needs_checking"

        extracted_fields = {
            k: v
            for k, v in data.items()
            if k not in ("verdict", "verdict_reason", "summary", "confidence")
        }

        return JudgeResult(
            verdict=verdict,
            extracted_fields=extracted_fields,
            verdict_reason=data.get("verdict_reason", ""),
            summary=data.get("summary", ""),
            confidence=data.get("confidence", "medium"),
            raw=data,
        )
