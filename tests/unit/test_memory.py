import pytest
from app.memory.manager import ConversationMemory


class TestConversationMemory:
    def test_add_message(self):
        memory = ConversationMemory(max_turns=5)
        memory.add_message("session1", "user", "Hello")
        
        history = memory.get_history("session1")
        assert len(history) == 1
        assert history[0].role == "user"
        assert history[0].content == "Hello"

    def test_get_history_empty(self):
        memory = ConversationMemory()
        history = memory.get_history("nonexistent")
        assert history == []

    def test_session_exists(self):
        memory = ConversationMemory()
        memory.add_message("session1", "user", "Hello")
        
        assert memory.session_exists("session1") is True
        assert memory.session_exists("session2") is False

    def test_max_turns_trimming(self):
        memory = ConversationMemory(max_turns=3)
        for i in range(5):
            memory.add_message("session1", "user", f"Message {i}")
        
        history = memory.get_history("session1")
        assert len(history) == 3

    def test_clear_session(self):
        memory = ConversationMemory()
        memory.add_message("session1", "user", "Hello")
        memory.clear_session("session1")
        
        assert memory.session_exists("session1") is False

    def test_get_history_as_dict(self):
        memory = ConversationMemory()
        memory.add_message("session1", "user", "Hello")
        
        history_dict = memory.get_history_as_dict("session1")
        assert len(history_dict) == 1
        assert history_dict[0]["role"] == "user"
        assert history_dict[0]["content"] == "Hello"
        assert "timestamp" in history_dict[0]

    def test_get_message_count(self):
        memory = ConversationMemory()
        memory.add_message("session1", "user", "Hello")
        memory.add_message("session1", "assistant", "Hi there")
        
        assert memory.get_message_count("session1") == 2
        assert memory.get_message_count("nonexistent") == 0