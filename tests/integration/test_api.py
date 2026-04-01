import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@patch("app.api.routes.get_agent_graph")
@patch("app.api.routes.get_memory")
def test_chat_endpoint(mock_memory, mock_graph, client):
    # Mock Memory
    memory_instance = MagicMock()
    mock_memory.return_value = memory_instance
    memory_instance.get_history_as_dict.return_value = []
    
    # Mock Agent Graph
    graph_instance = MagicMock()
    mock_graph.return_value = graph_instance
    
    # Mock Async response for ainvoke
    async def mock_ainvoke(*args, **kwargs):
        return {
            "response": "Hello, how can I help you?",
            "intent": "greeting",
            "sources": []
        }
    graph_instance.ainvoke = mock_ainvoke
    
    # Test Request
    request_data = {
        "session_id": "test_session",
        "message": "Hi"
    }
    
    response = client.post("/api/v1/chat", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test_session"
    assert data["message"] == "Hello, how can I help you?"
    assert data["intent"] == "greeting"

def test_delete_session(client):
    response = client.delete("/api/v1/sessions/test_session")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
