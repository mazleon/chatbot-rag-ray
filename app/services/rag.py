import logging
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        settings = get_settings()
        self.vectorstore_path = settings.vectorstore_path
        self.vectorstore_type = settings.vectorstore_type
        self.top_k = settings.top_k_retrieval
        self.similarity_threshold = settings.similarity_threshold
        
        logger.info(f"Initializing RAG service with provider: {settings.llm_provider}")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
        )
        
        # Use the correct API key based on provider
        api_key = settings.openrouter_api_key or settings.openai_api_key
        base_url = settings.openrouter_base_url if settings.llm_provider == "openrouter" else None
        
        logger.info(f"Embedding model: {settings.embedding_model}")
        
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=api_key,
            base_url=base_url,
        )
        
        self.vectorstore: Optional[Any] = None
        self._load_vectorstore()
    
    def _load_vectorstore(self) -> None:
        import os
        if os.path.exists(self.vectorstore_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.vectorstore_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
                logger.info(f"Loaded vector store from {self.vectorstore_path}")
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")
                self.vectorstore = None
        else:
            logger.warning(f"Vector store path does not exist: {self.vectorstore_path}")
    
    def ingest_documents(self, documents: List[str]) -> int:
        from langchain_core.documents import Document
        
        docs = [Document(page_content=doc) for doc in documents]
        chunks = self.text_splitter.split_documents(docs)
        
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vectorstore.add_documents(chunks)
        
        self._save_vectorstore()
        logger.info(f"Ingested {len(chunks)} chunks")
        return len(chunks)
    
    def _save_vectorstore(self) -> None:
        import os
        os.makedirs(self.vectorstore_path, exist_ok=True)
        if self.vectorstore:
            self.vectorstore.save_local(self.vectorstore_path)
            logger.info(f"Saved vector store to {self.vectorstore_path}")
    
    async def retrieve(self, query: str, k: Optional[int] = None, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        k = k or self.top_k
        
        if self.vectorstore is None:
            logger.warning("Vector store not initialized, returning empty results")
            return []
        
        try:
            logger.debug(f"Retrieving documents for query: {query[:50]}...")
            docs = self.vectorstore.similarity_search_with_score(query, k=k)
            results = []
            scores = []
            for doc, score in docs:
                results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 1 - score,
                })
                scores.append(1 - score)
            logger.info(f"Retrieved {len(results)} documents")
            
            from app.services.langfuse import get_langfuse_service
            langfuse = get_langfuse_service()
            if langfuse and langfuse.is_enabled() and session_id:
                langfuse.trace_retrieval(
                    session_id=session_id,
                    query=query,
                    documents=results,
                    scores=scores,
                )
            
            return results
        except Exception as e:
            logger.error(f"Error during retrieval: {e}", exc_info=True)
            from app.utils.exceptions import RAGRetrievalError
            raise RAGRetrievalError(str(e))


_rag_service = None


def get_rag_service() -> Optional[RAGService]:
    global _rag_service
    if _rag_service is None:
        try:
            _rag_service = RAGService()
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}", exc_info=True)
            _rag_service = None
    return _rag_service