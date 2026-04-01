import logging
import os
from typing import Optional, Dict, Any
from langfuse import get_client
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LangfuseService:
    def __init__(self):
        self.settings = get_settings()
        self.langfuse = None
        self._initialize()
    
    def _initialize(self):
        if not self.settings.langfuse_enabled:
            logger.info("LangFuse observability is disabled")
            return
        
        if not self.settings.langfuse_secret_key or not self.settings.langfuse_public_key:
            logger.warning("LangFuse credentials not configured")
            return
        
        try:
            os.environ["LANGFUSE_SECRET_KEY"] = self.settings.langfuse_secret_key
            os.environ["LANGFUSE_PUBLIC_KEY"] = self.settings.langfuse_public_key
            os.environ["LANGFUSE_HOST"] = self.settings.langfuse_base_url
            
            self.langfuse = get_client()
            
            logger.info(f"LangFuse initialized with base_url: {self.settings.langfuse_base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize LangFuse: {e}")
            self.langfuse = None
    
    def is_enabled(self) -> bool:
        return self.langfuse is not None
    
    def trace_generation(
        self,
        session_id: str,
        user_message: str,
        model: str,
        prompt: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        if not self.is_enabled():
            return
        
        try:
            with self.langfuse.start_as_current_observation(
                as_type="generation",
                name="llm-generation",
                model=model,
                input=user_message,
                output=response,
                metadata={"session_id": session_id, **(metadata or {})},
            ):
                pass
            self.langfuse.flush()
            logger.info(f"Traced LLM generation for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to trace generation: {e}")
    
    def trace_retrieval(
        self,
        session_id: str,
        query: str,
        documents: list,
        scores: Optional[list] = None,
    ):
        if not self.is_enabled():
            return
        
        try:
            with self.langfuse.start_as_current_observation(
                as_type="span",
                name="rag-retrieval",
                input=query,
                output={"document_count": len(documents)},
                metadata={"session_id": session_id},
            ):
                pass
            self.langfuse.flush()
            logger.info(f"Traced RAG retrieval for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to trace retrieval: {e}")
    
    def trace_agent_flow(
        self,
        session_id: str,
        user_message: str,
        intent: str,
        response: str,
        conversation_history: list,
    ):
        if not self.is_enabled():
            return
        
        try:
            with self.langfuse.start_as_current_observation(
                as_type="agent",
                name="agent-flow",
                input={"user_message": user_message, "intent": intent},
                output=response[:500],
                metadata={"session_id": session_id, "message_count": len(conversation_history)},
            ):
                pass
            self.langfuse.flush()
            logger.info(f"Traced agent flow for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to trace agent flow: {e}")


_langfuse_service: Optional[LangfuseService] = None


def get_langfuse_service() -> Optional[LangfuseService]:
    global _langfuse_service
    if _langfuse_service is None:
        _langfuse_service = LangfuseService()
    return _langfuse_service
