from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PromptStatus(StrEnum):
    SUCCESS = "SUCCESS"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"


class PromptRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    prompt: str = Field(min_length=1, max_length=2_000)
    targetLanguage: str
    contextId: UUID | None = None

    @field_validator("prompt")
    @classmethod
    def prompt_must_contain_text(cls, value: str) -> str:
        if not any(character.isalnum() for character in value):
            raise ValueError("prompt must contain letters or numbers")
        return value

    @field_validator("targetLanguage")
    @classmethod
    def language_must_be_supported(cls, value: str) -> str:
        supported_languages = {"de", "en", "es", "fr"}
        if value not in supported_languages:
            raise ValueError("Target language is not supported")
        return value


class Insight(BaseModel):
    id: UUID
    title: str
    content: str
    metadata: dict[str, Any]


class Pagination(BaseModel):
    page: int
    pageSize: int
    totalItems: int
    totalPages: int
    hasNextPage: bool


class PromptResponse(BaseModel):
    status: PromptStatus
    requestId: UUID
    contextId: UUID
    shouldCallAi: bool
    message: str | None = None


class InsightsResponse(BaseModel):
    insights: list[Insight]
    pagination: Pagination
