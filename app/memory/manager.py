import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    intent: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "intent": self.intent,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data.get("timestamp"), str) else datetime.now(),
            intent=data.get("intent"),
        )


class MemoryBackend(ABC):
    @abstractmethod
    def add_message(self, session_id: str, role: str, content: str, intent: Optional[str] = None) -> None:
        pass
    
    @abstractmethod
    def get_history(self, session_id: str) -> List[Message]:
        pass
    
    @abstractmethod
    def clear_session(self, session_id: str) -> None:
        pass
    
    @abstractmethod
    def session_exists(self, session_id: str) -> bool:
        pass


class InMemoryBackend(MemoryBackend):
    def __init__(self, max_turns: int = 10):
        self.sessions: Dict[str, List[Message]] = {}
        self.max_turns = max_turns
    
    def add_message(self, session_id: str, role: str, content: str, intent: Optional[str] = None) -> None:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(Message(role=role, content=content, intent=intent))
        if len(self.sessions[session_id]) > self.max_turns:
            self.sessions[session_id] = self.sessions[session_id][-self.max_turns:]
    
    def get_history(self, session_id: str) -> List[Message]:
        return self.sessions.get(session_id, [])
    
    def clear_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)
    
    def session_exists(self, session_id: str) -> bool:
        return session_id in self.sessions


class RedisBackend(MemoryBackend):
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self._redis = None
        self._connect()
    
    def _connect(self):
        try:
            import redis
            settings = get_settings()
            self._redis = redis.from_url(settings.redis_url, db=settings.redis_db, decode_responses=True)
            self._redis.ping()
            logger.info("Redis memory backend connected")
        except Exception as e:
            logger.warning(f"Redis connection failed, falling back to in-memory: {e}")
            self._redis = None
    
    def _get_key(self, session_id: str) -> str:
        return f"chat:session:{session_id}"
    
    def add_message(self, session_id: str, role: str, content: str, intent: Optional[str] = None) -> None:
        if not self._redis:
            return
        
        key = self._get_key(session_id)
        message = Message(role=role, content=content, intent=intent)
        
        self._redis.rpush(key, json.dumps(message.to_dict()))
        self._redis.ltrim(key, -self.max_turns, -1)
    
    def get_history(self, session_id: str) -> List[Message]:
        if not self._redis:
            return []
        
        key = self._get_key(session_id)
        data = self._redis.lrange(key, 0, -1)
        
        return [Message.from_dict(json.loads(item)) for item in data]
    
    def clear_session(self, session_id: str) -> None:
        if self._redis:
            self._redis.delete(self._get_key(session_id))
    
    def session_exists(self, session_id: str) -> bool:
        if not self._redis:
            return False
        return self._redis.exists(self._get_key(session_id)) > 0


class ConversationMemory:
    def __init__(self, backend: Optional[MemoryBackend] = None):
        settings = get_settings()
        
        if backend:
            self.backend = backend
        elif settings.redis_url:
            try:
                self.backend = RedisBackend(max_turns=settings.session_max_turns)
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}")
                self.backend = InMemoryBackend(max_turns=settings.session_max_turns)
        else:
            self.backend = InMemoryBackend(max_turns=settings.session_max_turns)
        
        logger.info(f"Using memory backend: {type(self.backend).__name__}")
    
    def add_message(self, session_id: str, role: str, content: str, intent: Optional[str] = None) -> None:
        self.backend.add_message(session_id, role, content, intent)
    
    def get_history(self, session_id: str) -> List[Message]:
        return self.backend.get_history(session_id)
    
    def get_history_as_dict(self, session_id: str) -> List[Dict]:
        return [m.to_dict() for m in self.get_history(session_id)]
    
    def clear_session(self, session_id: str) -> None:
        self.backend.clear_session(session_id)
    
    def session_exists(self, session_id: str) -> bool:
        return self.backend.session_exists(session_id)
    
    def get_message_count(self, session_id: str) -> int:
        return len(self.get_history(session_id))


memory = ConversationMemory()


def get_memory() -> ConversationMemory:
    return memory
