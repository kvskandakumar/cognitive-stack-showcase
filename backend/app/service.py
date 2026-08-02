from typing import Any
from uuid import UUID, uuid4

from .repository import PromptRepository
from .schemas import PromptRequest, PromptResponse, PromptStatus


INSIGHT_TEMPLATES = [
    ("Audience alignment", "Define the target audience before selecting a response format.", "strategy", "high"),
    ("Make the outcome measurable", "Add a concrete success metric so the result can be evaluated.", "measurement", "high"),
    ("Add supporting context", "Include relevant constraints and background information.", "context", "medium"),
    ("Prefer clear instructions", "Use direct, unambiguous language for each requested task.", "quality", "medium"),
    ("Separate complex tasks", "Break multi-part work into ordered steps with explicit deliverables.", "workflow", "medium"),
    ("Specify the output shape", "Describe the expected structure, length, and tone.", "format", "high"),
    ("Provide an example", "A representative example can remove ambiguity.", "context", "low"),
    ("Identify constraints", "State technical, legal, or business constraints.", "risk", "high"),
    ("Review assumptions", "Call out assumptions that may change the recommendation.", "quality", "medium"),
    ("Use consistent terminology", "Keep domain terms consistent throughout the response.", "quality", "low"),
    ("Request sources", "Ask for references when claims need verification.", "research", "medium"),
    ("Plan for iteration", "Reserve a follow-up step for stakeholder feedback.", "workflow", "low"),
]


class PromptService:
    def __init__(self, repository: PromptRepository) -> None:
        self.repository = repository

    @staticmethod
    def needs_clarification(prompt: str) -> bool:
        normalized = prompt.casefold()
        vague_phrases = ("clarify", "something", "anything", "help me")
        return (
            len(prompt) < 5
            or len(prompt.split()) < 3
            or any(phrase in normalized for phrase in vague_phrases)
        )

    @staticmethod
    def dummy_insights(language: str) -> list[dict[str, Any]]:
        return [
            {
                "id": uuid4(),
                "title": title,
                "content": content,
                "metadata": {"category": category, "priority": priority, "language": language},
            }
            for title, content, category, priority in INSIGHT_TEMPLATES
        ]

    def process(self, request: PromptRequest) -> PromptResponse:
        request_id = uuid4()
        context_id = request.contextId or uuid4()
        needs_clarification = self.needs_clarification(request.prompt)
        status = PromptStatus.NEEDS_CLARIFICATION if needs_clarification else PromptStatus.SUCCESS
        insights = [] if needs_clarification else self.dummy_insights(request.targetLanguage)

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
