import pytest
from unittest.mock import MagicMock, patch
from app.services.rag import RAGService
from app.utils.exceptions import RAGRetrievalError

@pytest.fixture
def mock_settings():
    with patch("app.services.rag.get_settings") as mock:
        settings = MagicMock()
        settings.vectorstore_path = "/tmp/test_vectorstore"
        settings.vectorstore_type = "faiss"
        settings.top_k_retrieval = 3
        settings.similarity_threshold = 0.7
        settings.embedding_model = "text-embedding-3-small"
        settings.openai_api_key = "test-key"
        mock.return_value = settings
        yield settings

@pytest.fixture
def rag_service(mock_settings):
    with patch("app.services.rag.OpenAIEmbeddings"), \
         patch("app.services.rag.FAISS.load_local") as mock_load:
        mock_load.return_value = MagicMock()
        service = RAGService()
        yield service

def test_rag_service_init(rag_service, mock_settings):
    assert rag_service.vectorstore_path == mock_settings.vectorstore_path
    assert rag_service.top_k == mock_settings.top_k_retrieval

@pytest.mark.asyncio
async def test_retrieve_empty_vectorstore(rag_service):
    rag_service.vectorstore = None
    results = await rag_service.retrieve("test query")
    assert results == []

@pytest.mark.asyncio
async def test_retrieve_with_results(rag_service):
    mock_doc = MagicMock()
    mock_doc.page_content = "This is a test policy"
    mock_doc.metadata = {"source": "test.txt"}
    
    rag_service.vectorstore = MagicMock()
    rag_service.vectorstore.similarity_search_with_score.return_value = [(mock_doc, 0.1)]
    
    results = await rag_service.retrieve("test query")
    
    assert len(results) == 1
    assert results[0]["text"] == "This is a test policy"
    assert results[0]["score"] == 0.9  # 1 - 0.1

@pytest.mark.asyncio
async def test_retrieve_raises_error(rag_service):
    rag_service.vectorstore = MagicMock()
    rag_service.vectorstore.similarity_search_with_score.side_effect = Exception("FAISS Error")
    
    with pytest.raises(RAGRetrievalError):
        await rag_service.retrieve("query")

def test_ingest_documents(rag_service):
    with patch("app.services.rag.FAISS.from_documents") as mock_from_docs, \
         patch("app.services.rag.RAGService._save_vectorstore"):
        
        mock_from_docs.return_value = MagicMock()
        rag_service.vectorstore = None
        
        count = rag_service.ingest_documents(["Doc 1", "Doc 2"])
        
        assert count > 0
        mock_from_docs.assert_called_once()
