import os
from typing import Protocol

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, AuthenticationError, RateLimitError
from pydantic import BaseModel, Field


class GeneratedInsight(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    content: str = Field(min_length=1, max_length=1_500)
    category: str = Field(min_length=1, max_length=80)
    priority: str = Field(pattern=r"^(low|medium|high)$")


class GeneratedInsights(BaseModel):
    insights: list[GeneratedInsight] = Field(min_length=1, max_length=12)


class InsightGenerator(Protocol):
    async def generate(self, prompt: str, target_language: str) -> GeneratedInsights: ...


class AIServiceError(Exception):
    def __init__(self, error: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.error = error
        self.message = message
        self.status_code = status_code


class MockInsightGenerator:
    """Deterministic, production-shaped results for local and demo environments."""

    async def generate(self, prompt: str, target_language: str) -> GeneratedInsights:
        subject = prompt.rstrip(".?!")
        templates = [
            ("Clarify the primary outcome", f"Define the measurable outcome expected from: {subject}.", "strategy", "high"),
            ("Identify the target audience", "Document the audience, their needs, and the context in which they will use the result.", "audience", "high"),
            ("Set measurable success criteria", "Choose specific quality, adoption, or performance metrics before implementation begins.", "measurement", "high"),
            ("Capture key constraints", "List the budget, timeline, technical, regulatory, and operational boundaries.", "risk", "high"),
            ("Break delivery into phases", "Organize the work into discovery, implementation, validation, and rollout stages.", "workflow", "medium"),
            ("Validate assumptions early", "Test the highest-impact assumptions with representative users or stakeholders.", "validation", "high"),
            ("Define the output format", "Specify the expected structure, level of detail, tone, and delivery channel.", "format", "medium"),
            ("Plan stakeholder reviews", "Assign owners and decision points so feedback arrives before costly commitments.", "collaboration", "medium"),
            ("Compare viable alternatives", "Evaluate at least two approaches using consistent cost, risk, and impact criteria.", "strategy", "medium"),
            ("Prepare for edge cases", "Identify failure scenarios and define graceful fallback behavior for each one.", "risk", "medium"),
            ("Track decisions", "Record important choices, supporting evidence, owners, and follow-up dates.", "governance", "low"),
            ("Create an iteration loop", "Use observed results and stakeholder feedback to prioritize the next improvement.", "workflow", "medium"),
        ]
        return GeneratedInsights(
            insights=[
                GeneratedInsight(
                    title=title,
                    content=content,
                    category=category,
                    priority=priority,
                )
                for title, content, category, priority in templates
            ]
        )


class OpenAIInsightGenerator:
    def __init__(self, client: AsyncOpenAI | None = None, model: str | None = None) -> None:
        self._client = client
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

    def _get_client(self) -> AsyncOpenAI:
        if self._client is not None:
            return self._client
        if not os.getenv("OPENAI_API_KEY"):
            raise AIServiceError(
                "AI_NOT_CONFIGURED",
                "The AI service is not configured on the server",
                503,
            )
        self._client = AsyncOpenAI(timeout=45.0, max_retries=2)
        return self._client

    async def generate(self, prompt: str, target_language: str) -> GeneratedInsights:
        try:
            response = await self._get_client().responses.parse(
                model=self.model,
                reasoning={"effort": "low"},
                input=[
                    {
                        "role": "developer",
                        "content": (
                            "Analyze the user's request and return 6 to 12 useful, distinct insights. "
                            "Write every title and content field in the requested target language. "
                            "Use a short category and set priority to low, medium, or high."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Target language: {target_language}\n\nRequest:\n{prompt}",
                    },
                ],
                text_format=GeneratedInsights,
            )
        except AuthenticationError as exc:
            raise AIServiceError("AI_AUTHENTICATION_FAILED", "The AI service credentials are invalid", 502) from exc
        except RateLimitError as exc:
            error_code = exc.body.get("code") if isinstance(exc.body, dict) else None
            if error_code == "insufficient_quota":
                raise AIServiceError(
                    "AI_QUOTA_EXCEEDED",
                    "The OpenAI account has no available API quota. Check billing and usage limits.",
                    429,
                ) from exc
            raise AIServiceError("AI_RATE_LIMITED", "The AI service is temporarily rate limited", 429) from exc
        except APIConnectionError as exc:
            raise AIServiceError("AI_UNAVAILABLE", "Unable to connect to the AI service", 503) from exc
        except APIStatusError as exc:
            raise AIServiceError("AI_PROVIDER_ERROR", "The AI service could not process the request", 502) from exc

        if response.output_parsed is None:
            raise AIServiceError("AI_INVALID_RESPONSE", "The AI service returned an invalid response", 502)
        return response.output_parsed
