import math
import os
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .ai_service import (
    AIServiceError,
    GeminiInsightGenerator,
    InsightGenerator,
    MockInsightGenerator,
)
from .repository import PromptRepository
from .schemas import InsightsResponse, Pagination, PromptRequest, PromptResponse
from .service import PromptService


load_dotenv()


def configured_insight_generator() -> InsightGenerator:
    use_real_geminiai = os.getenv("USE_REAL_GEMINIAI", os.getenv("USE_REAL_OPENAI", "false")).strip().casefold()
    print(f"USE_REAL_GEMINIAI={use_real_geminiai}")
    if use_real_geminiai in {"1", "true", "yes", "on"}:
        return GeminiInsightGenerator()
    print("Using MockInsightGenerator for insights. Set USE_REAL_GEMINIAI=true to use Gemini.")
    return MockInsightGenerator()


def create_app(
    database_path: Path | None = None,
    insight_generator: InsightGenerator | None = None,
) -> FastAPI:
    path = database_path or Path(os.getenv("DATABASE_PATH", "backend/data/prompts.db"))
    repository = PromptRepository(path)
    service = PromptService(repository, insight_generator or configured_insight_generator())
    app = FastAPI(title="AI Middleware API", version="1.0.0")
    app.state.repository = repository
    app.state.prompt_service = service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:5174"
        ).split(","),
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        invalid_fields = {str(error["loc"][1]) for error in exc.errors() if len(error["loc"]) > 1}

        if "targetLanguage" in invalid_fields:
            content = {"error": "INVALID_LANGUAGE", "message": "Target language is not supported"}
        elif "prompt" in invalid_fields:
            content = {"error": "INVALID_PROMPT", "message": "Prompt is required and must contain text"}
        elif "contextId" in invalid_fields:
            content = {"error": "INVALID_CONTEXT_ID", "message": "Context ID must be a valid UUID"}
        else:
            content = {"error": "INVALID_REQUEST", "message": "Request body is invalid"}

        return JSONResponse(status_code=422, content=content)

    @app.exception_handler(AIServiceError)
    async def ai_service_error_handler(_: Request, exc: AIServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.error, "message": exc.message},
        )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/prompts", response_model=PromptResponse, status_code=201)
    async def submit_prompt(request: Request, payload: PromptRequest) -> PromptResponse:
        return await request.app.state.prompt_service.process(payload)

    @app.get("/api/prompts/{request_id}/insights", response_model=InsightsResponse)
    async def get_insights(
        request: Request,
        request_id: UUID,
        page: int = Query(default=1, ge=1),
        limit: int = Query(default=6, ge=1, le=100),
    ) -> InsightsResponse:
        result = request.app.state.repository.get_insights(request_id, page, limit)
        if result is None:
            raise HTTPException(status_code=404, detail="Prompt request not found.")
        insights, total = result
        total_pages = math.ceil(total / limit) if total else 0
        return InsightsResponse(
            insights=insights,
            pagination=Pagination(
                page=page,
                pageSize=limit,
                totalItems=total,
                totalPages=total_pages,
                hasNextPage=page < total_pages,
            ),
        )

    return app


app = create_app()
