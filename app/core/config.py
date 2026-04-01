from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Life Insurance Agent"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # LLM Provider: "openai" or "openrouter"
    llm_provider: str = "openrouter"

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2000

    # OpenRouter
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "google/gemini-flash-1.5-8b"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Embeddings
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Vector Store
    vectorstore_path: str = "./vectorstore"
    vectorstore_type: str = "faiss"

    # RAG
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.7

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0

    # LangFuse Observability
    langfuse_secret_key: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_base_url: str = "https://us.cloud.langfuse.com"
    langfuse_enabled: bool = False

    # Session
    session_max_turns: int = 10
    session_timeout: int = 3600

    cors_origins: list[str] = ["*"]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"

    def get_log_level(self) -> str:
        if self.app_env.lower() == "production":
            return "WARNING"
        return self.log_level

    def get_cors_origins(self) -> list[str]:
        if self.app_env.lower() == "production":
            return self.cors_origins or []
        return ["*"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()