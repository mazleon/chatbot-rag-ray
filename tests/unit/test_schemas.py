import pytest
from app.models.schemas import ChatRequest, ChatResponse, HealthResponse


class TestSchemas:
    def test_chat_request_valid(self):
        request = ChatRequest(session_id="test123", message="Hello")
        assert request.session_id == "test123"
        assert request.message == "Hello"

    def test_chat_request_with_context(self):
        request = ChatRequest(
            session_id="test123",
            message="Hello",
            context={"key": "value"}
        )
        assert request.context == {"key": "value"}

    def test_chat_request_message_length_validation(self):
        with pytest.raises(ValueError):
            ChatRequest(session_id="test", message="")

    def test_chat_response(self):
        response = ChatResponse(
            session_id="test123",
            message="Hello there",
            intent="greeting"
        )
        assert response.session_id == "test123"
        assert response.message == "Hello there"
        assert response.intent == "greeting"

    def test_health_response(self):
        response = HealthResponse(status="healthy", version="1.0.0", environment="test")
        assert response.status == "healthy"
        assert response.version == "1.0.0"