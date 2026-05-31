import pytest
from unittest.mock import MagicMock, patch
from judge.judge_agent import JudgeAgent, JudgeResult

MOCK_HOUSING_RESPONSE = """{
  "location": "Bellevue",
  "rent": 950,
  "utilities_included": true,
  "move_in_date": "June 1, 2026",
  "duration": "long_term",
  "transit_access": "good",
  "gender_preference": "female",
  "confidence": "high",
  "summary": "A room for rent in Bellevue at $950/month utilities included, available June 1.",
  "verdict": "worth_checking",
  "verdict_reason": "Location, rent, and move-in date all match criteria."
}"""

MOCK_IGNORE_RESPONSE = """{
  "location": "Seattle",
  "rent": 1500,
  "utilities_included": false,
  "move_in_date": "August 1, 2026",
  "duration": "long_term",
  "transit_access": "limited",
  "gender_preference": "any",
  "confidence": "high",
  "summary": "A room in Seattle at $1500/month, available August 1.",
  "verdict": "ignore",
  "verdict_reason": "Rent exceeds maximum budget and location does not match."
}"""


@pytest.fixture
def agent():
    with patch("judge.judge_agent.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield JudgeAgent(api_key="test-key"), mock_client


def test_judge_returns_worth_checking(agent):
    judge, mock_client = agent
    mock_response = MagicMock()
    mock_response.text = MOCK_HOUSING_RESPONSE
    mock_client.models.generate_content.return_value = mock_response

    criteria = {
        "locations": ["Bellevue", "Redmond"],
        "max_rent": 1000,
        "move_in_within_days": 30,
    }

    result = judge.judge(
        body="벨뷰 룸 렌트합니다. 월 $950 유틸포함. 6월 1일 입주 가능.",
        category="housing",
        criteria=criteria,
    )

    assert isinstance(result, JudgeResult)
    assert result.verdict == "worth_checking"
    assert result.extracted_fields["location"] == "Bellevue"
    assert result.extracted_fields["rent"] == 950
    assert result.confidence == "high"


def test_judge_returns_ignore(agent):
    judge, mock_client = agent
    mock_response = MagicMock()
    mock_response.text = MOCK_IGNORE_RESPONSE
    mock_client.models.generate_content.return_value = mock_response

    criteria = {
        "locations": ["Bellevue", "Redmond"],
        "max_rent": 1000,
        "move_in_within_days": 30,
    }

    result = judge.judge(
        body="시애틀 룸 렌트합니다. 월 $1500. 8월 1일 입주 가능.",
        category="housing",
        criteria=criteria,
    )

    assert result.verdict == "ignore"
    assert result.verdict_reason != ""


def test_judge_handles_code_block_response(agent):
    judge, mock_client = agent
    mock_response = MagicMock()
    mock_response.text = f"```json\n{MOCK_HOUSING_RESPONSE}\n```"
    mock_client.models.generate_content.return_value = mock_response

    result = judge.judge(
        body="벨뷰 룸 렌트합니다.",
        category="housing",
        criteria={"locations": ["Bellevue"], "max_rent": 1000},
    )

    assert result.verdict == "worth_checking"


def test_judge_invalid_verdict_defaults_to_needs_checking(agent):
    judge, mock_client = agent
    mock_response = MagicMock()
    mock_response.text = """{
        "location": "Bellevue",
        "rent": 950,
        "confidence": "medium",
        "summary": "Test",
        "verdict": "invalid_value",
        "verdict_reason": "test"
    }"""
    mock_client.models.generate_content.return_value = mock_response

    result = judge.judge(
        body="test",
        category="housing",
        criteria={},
    )

    assert result.verdict == "needs_checking"
