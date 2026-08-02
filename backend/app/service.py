from typing import Any
from uuid import UUID, uuid4

from .repository import PromptRepository
from .schemas import PromptRequest, PromptResponse, PromptStatus
from .ai_service import InsightGenerator


class PromptService:
    def __init__(self, repository: PromptRepository, insight_generator: InsightGenerator) -> None:
        self.repository = repository
        self.insight_generator = insight_generator

    @staticmethod
    def needs_clarification(prompt: str) -> bool:
        normalized = prompt.casefold()
        vague_phrases = ("clarify", "something", "anything", "help me")
        return (
            len(prompt) < 5
            or len(prompt.split()) < 3
            or any(phrase in normalized for phrase in vague_phrases)
        )

    async def process(self, request: PromptRequest) -> PromptResponse:
        request_id = uuid4()
        context_id = request.contextId or uuid4()
        needs_clarification = self.needs_clarification(request.prompt)
        status = PromptStatus.NEEDS_CLARIFICATION if needs_clarification else PromptStatus.SUCCESS
        insights: list[dict[str, Any]] = []
        if not needs_clarification:
            generated = await self.insight_generator.generate(request.prompt, request.targetLanguage)
            insights = [
                {
                    "id": uuid4(),
                    "title": insight.title,
                    "content": insight.content,
                    "metadata": {
                        "category": insight.category,
                        "priority": insight.priority,
                        "language": request.targetLanguage,
                    },
                }
                for insight in generated.insights
            ]

        self.repository.save_prompt(
            request_id=request_id,
            context_id=context_id,
            prompt=request.prompt,
            target_language=request.targetLanguage,
            status=status.value,
            should_call_ai=not needs_clarification,
            insights=insights,
        )
        return PromptResponse(
            status=status,
            requestId=request_id,
            contextId=context_id,
            shouldCallAi=not needs_clarification,
            message=("Please provide more details" if needs_clarification else None),
        )
