from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., min_length=1, max_length=2000)
    context: Optional[Dict[str, Any]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "abc123",
                "message": "What is term life insurance?"
            }
        }
    }


class ChatResponse(BaseModel):
    session_id: str
    message: str
    intent: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "abc123",
                "message": "Term life insurance provides coverage for a specific period...",
                "intent": "policy_info",
                "sources": [{"text": "...", "score": 0.95}]
            }
        }
    }


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class DocumentIngestRequest(BaseModel):
    documents: List[str] = Field(..., description="List of document texts to ingest")
    metadata: Optional[Dict[str, Any]] = None


class DocumentIngestResponse(BaseModel):
    status: str
    chunks_created: int
    message: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    message_count: int


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


class FileUploadRequest(BaseModel):
    filename: str
    content: str
    file_type: Optional[str] = None