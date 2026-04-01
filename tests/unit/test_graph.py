import pytest
from app.agents.graph import AgentState, classify_node, retrieve_node
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_classify_node_premium():
    state = AgentState(messages=[{"role": "user", "content": "How much is the premium?"}])
    result = await classify_node(state)
    assert result.intent == "premium"

@pytest.mark.asyncio
async def test_classify_node_claims():
    state = AgentState(messages=[{"role": "user", "content": "I want to file a claim"}])
    result = await classify_node(state)
    assert result.intent == "claims"

@pytest.mark.asyncio
async def test_classify_node_general():
    state = AgentState(messages=[{"role": "user", "content": "Hello there"}])
    result = await classify_node(state)
    assert result.intent == "general"

@pytest.mark.asyncio
async def test_retrieve_node_logic():
    # Setup mock RAG
    mock_rag = MagicMock()
    mock_rag.vectorstore = MagicMock()
    mock_rag.retrieve = AsyncMock(return_value=[{"text": "policy details", "score": 0.9}])
    
    state = AgentState(
        messages=[{"role": "user", "content": "Tell me about my policy"}],
        intent="policy_info"
    )
    
    # Patch the function called INSIDE retrieve_node
    # Since retrieve_node does 'from app.services.rag import get_rag_service'
    # we patch that service path.
    with patch("app.services.rag.get_rag_service", return_value=mock_rag):
        result = await retrieve_node(state)
    
    assert len(result.retrieved_docs) == 1
    assert result.retrieved_docs[0]["text"] == "policy details"
    mock_rag.retrieve.assert_called_once()

@pytest.mark.asyncio
async def test_retrieve_node_skip_general():
    state = AgentState(
        messages=[{"role": "user", "content": "Hi"}],
        intent="general"
    )
    
    with patch("app.services.rag.get_rag_service") as mock_get_rag:
        result = await retrieve_node(state)
        assert len(result.retrieved_docs) == 0
        mock_get_rag.assert_not_called()
