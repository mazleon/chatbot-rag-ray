import logging
import base64
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SessionHistoryResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
    FileUploadRequest,
)
from app.memory.manager import get_memory
from app.core.constants import API_VERSION
from app.api.routes import chat_endpoint
from app.services.rag import get_rag_service
from app.services.parser import parse_file

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", version=API_VERSION, environment="development")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        return await chat_endpoint(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    memory = get_memory()
    if not memory.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    history = memory.get_history_as_dict(session_id)
    return SessionHistoryResponse(
        session_id=session_id,
        messages=history,
        message_count=len(history)
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    memory = get_memory()
    memory.clear_session(session_id)
    return {"status": "deleted", "session_id": session_id}


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_documents(request: DocumentIngestRequest):
    try:
        rag_service = get_rag_service()
        if not rag_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service unavailable"
            )
        
        chunks = rag_service.ingest_documents(request.documents)
        return DocumentIngestResponse(
            status="success",
            chunks_created=chunks,
            message=f"Successfully ingested {len(request.documents)} documents"
        )
    except Exception as e:
        logger.error(f"Ingest endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.post("/upload", response_model=DocumentIngestResponse)
async def upload_document(request: FileUploadRequest):
    try:
        rag_service = get_rag_service()
        if not rag_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service unavailable"
            )
        
        file_bytes = base64.b64decode(request.content)
        
        text = parse_file(file_bytes, request.filename)
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not extract text from {request.filename}"
            )
        
        chunks = rag_service.ingest_documents([text])
        logger.info(f"Uploaded {request.filename}: {chunks} chunks created")
        
        return DocumentIngestResponse(
            status="success",
            chunks_created=chunks,
            message=f"Successfully processed {request.filename}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )