from uuid import uuid4

import httpx
import pytest

from backend.app.main import create_app
from backend.app.ai_service import GeneratedInsight, GeneratedInsights


@pytest.fixture
def anyio_backend():
    return "asyncio"


class FakeInsightGenerator:
    def __init__(self):
        self.calls = 0

    async def generate(self, prompt, target_language):
        self.calls += 1
        return GeneratedInsights(
            insights=[
                GeneratedInsight(
                    title=f"Insight {index}",
                    content=f"Result for {prompt}",
                    category="analysis",
                    priority="medium",
                )
                for index in range(12)
            ]
        )


def client(tmp_path, generator=None):
    app = create_app(tmp_path / "test.db", insight_generator=generator or FakeInsightGenerator())
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


@pytest.mark.anyio
async def test_submit_prompt_and_get_paginated_insights(tmp_path):
    context_id = uuid4()
    async with client(tmp_path) as api:
        response = await api.post(
            "/api/prompts",
            json={"prompt": "Create a detailed launch strategy", "targetLanguage": "en", "contextId": str(context_id)},
        )
        body = response.json()
        insights = await api.get(f'/api/prompts/{body["requestId"]}/insights?page=1&limit=5')
    assert response.status_code == 201
    assert body["status"] == "SUCCESS"
    assert body["shouldCallAi"] is True
    assert body["contextId"] == str(context_id)

    assert insights.status_code == 200
    assert len(insights.json()["insights"]) == 5
    assert insights.json()["pagination"] == {
        "page": 1, "pageSize": 5, "totalItems": 12, "totalPages": 3, "hasNextPage": True
    }


@pytest.mark.anyio
async def test_vague_prompt_does_not_trigger_ai_decision(tmp_path):
    generator = FakeInsightGenerator()
    async with client(tmp_path, generator) as api:
        response = await api.post("/api/prompts", json={"prompt": "Help me", "targetLanguage": "fr"})
    assert response.status_code == 201
    assert response.json()["status"] == "NEEDS_CLARIFICATION"
    assert response.json()["shouldCallAi"] is False
    assert response.json()["message"] == "Please provide more details"
    assert generator.calls == 0

    async with client(tmp_path, generator) as api:
        short_response = await api.post("/api/prompts", json={"prompt": "abcd", "targetLanguage": "de"})
        insights = await api.get(f'/api/prompts/{short_response.json()["requestId"]}/insights')
    assert short_response.json()["status"] == "NEEDS_CLARIFICATION"
    assert insights.json()["pagination"]["totalItems"] == 0
    assert generator.calls == 0


@pytest.mark.anyio
async def test_empty_prompt_returns_structured_validation_error(tmp_path):
    async with client(tmp_path) as api:
        response = await api.post("/api/prompts", json={"prompt": "  ", "targetLanguage": "en"})
    assert response.status_code == 422
    assert response.json() == {
        "error": "INVALID_PROMPT",
        "message": "Prompt is required and must contain text",
    }


@pytest.mark.anyio
async def test_unsupported_language_returns_structured_validation_error(tmp_path):
    async with client(tmp_path) as api:
        response = await api.post(
            "/api/prompts", json={"prompt": "Create a detailed launch strategy", "targetLanguage": "it"}
        )
    assert response.status_code == 422
    assert response.json() == {
        "error": "INVALID_LANGUAGE",
        "message": "Target language is not supported",
    }


@pytest.mark.anyio
async def test_missing_prompt_and_invalid_context_are_rejected(tmp_path):
    async with client(tmp_path) as api:
        missing = await api.post("/api/prompts", json={"targetLanguage": "en"})
        invalid_context = await api.post(
            "/api/prompts",
            json={"prompt": "Create a detailed launch strategy", "targetLanguage": "en", "contextId": "invalid"},
        )
    assert missing.status_code == 422
    assert missing.json()["error"] == "INVALID_PROMPT"
    assert invalid_context.status_code == 422
    assert invalid_context.json()["error"] == "INVALID_CONTEXT_ID"
