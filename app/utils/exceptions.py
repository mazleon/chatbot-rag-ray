class AgentError(Exception):
    """Base exception for agent-related errors."""

    def __init__(self, message: str, error_code: str = "AGENT_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class RAGRetrievalError(AgentError):
    """Raised when RAG retrieval fails."""

    def __init__(self, message: str = "Failed to retrieve documents from knowledge base"):
        super().__init__(message, "RAG_RETRIEVAL_ERROR")


class LLMGenerationError(AgentError):
    """Raised when LLM generation fails."""

    def __init__(self, message: str = "Failed to generate response from LLM"):
        super().__init__(message, "LLM_GENERATION_ERROR")


class SessionNotFoundError(AgentError):
    """Raised when session does not exist."""

    def __init__(self, message: str = "Session not found"):
        super().__init__(message, "SESSION_NOT_FOUND")


class VectorStoreError(AgentError):
    """Raised when vector store operations fail."""

    def __init__(self, message: str = "Vector store operation failed"):
        super().__init__(message, "VECTOR_STORE_ERROR")


class EmbeddingError(AgentError):
    """Raised when embedding generation fails."""

    def __init__(self, message: str = "Failed to generate embeddings"):
        super().__init__(message, "EMBEDDING_ERROR")