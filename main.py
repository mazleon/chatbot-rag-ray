import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.constants import API_TITLE, API_VERSION, API_DESCRIPTION
from app.api.router import router
from app.utils.exceptions import (
    AgentError,
    RAGRetrievalError,
    LLMGenerationError,
    SessionNotFoundError,
    VectorStoreError,
    EmbeddingError,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {API_TITLE} v{API_VERSION}")
    logger.info(f"Environment: {get_settings().app_env}")
    logger.info(f"LLM Provider: {get_settings().llm_provider}")
    yield
    logger.info("Shutting down application")


settings = get_settings()
setup_logging(level=settings.log_level)

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AgentError)
async def agent_exception_handler(request: Request, exc: AgentError):
    logger.warning(f"Agent error: {exc.message}", extra={"error_code": exc.error_code})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": exc.error_code, "detail": exc.message},
    )


@app.exception_handler(SessionNotFoundError)
async def session_not_found_handler(request: Request, exc: SessionNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": exc.error_code, "detail": exc.message},
    )


@app.exception_handler(RAGRetrievalError)
async def rag_error_handler(request: Request, exc: RAGRetrievalError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": exc.error_code, "detail": exc.message},
    )


@app.exception_handler(LLMGenerationError)
async def llm_error_handler(request: Request, exc: LLMGenerationError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": exc.error_code, "detail": exc.message},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "method": request.method,
            "url": str(request.url),
            "path_params": request.path_params,
            "query_params": dict(request.query_params),
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {
        "message": "Life Insurance AI Support Agent API",
        "version": API_VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )