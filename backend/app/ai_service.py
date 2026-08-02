import os
from typing import Protocol

from google import genai
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
        print("MockInsightGenerator Class generate method called with prompt:", prompt)
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


class GeminiInsightGenerator:
    def __init__(self, client: object | None = None, model: str | None = None) -> None:
        self._client = client
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    def _get_client(self) -> object:
        if self._client is not None:
            return self._client
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise AIServiceError(
                "AI_NOT_CONFIGURED",
                "The AI service is not configured on the server",
                503,
            )
        self._client = genai.Client(api_key=api_key)
        return self._client

    async def generate(self, prompt: str, target_language: str) -> GeneratedInsights:
        print("------- GeminiInsightGenerator Class generate -------", prompt)
        try:
            response = self._get_client().models.generate_content(
                model=self.model,
                contents=(
                    "Analyze the user's request and return 6 to 12 useful, distinct insights. "
                    "Write every title and content field in the requested target language. "
                    "Use a short category and set priority to low, medium, or high.\n\n"
                    f"Target language: {target_language}\n\nRequest:\n{prompt}"
                ),
                config={
                    "response_mime_type": "application/json",
                    "response_schema": GeneratedInsights,
                },
            )
        except Exception as e:
            # get the error message from the exception and log it
            print(f"Error generating insights with Gemini: {e}")
            return await MockInsightGenerator().generate(prompt, target_language)

        text = getattr(response, "text", None)
        if not text:
            print("No text found in Gemini response. Falling back to MockInsightGenerator.")
            return await MockInsightGenerator().generate(prompt, target_language)

        try:
            return GeneratedInsights.model_validate_json(text)
        except Exception:
            print("Error validating Gemini response. Falling back to MockInsightGenerator.")
            return await MockInsightGenerator().generate(prompt, target_language)
