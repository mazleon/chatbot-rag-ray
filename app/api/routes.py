import logging
import uuid
from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.memory.manager import get_memory
from app.agents.graph import get_agent_graph

logger = logging.getLogger(__name__)


async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    memory = get_memory()
    
    session_id = request.session_id or str(uuid.uuid4())
    logger.info(f"Chat request for session: {session_id}")
    
    memory.add_message(session_id=session_id, role="user", content=request.message)
    logger.info(f"User message added, checking history...")
    
    history = memory.get_history_as_dict(session_id)
    logger.info(f"History retrieved for session {session_id}: {len(history)} messages")
    for i, h in enumerate(history):
        logger.info(f"  History[{i}]: {h.get('role')} - {h.get('content', '')[:50]}")
    
    agent_graph = get_agent_graph()
    result = await agent_graph.ainvoke(
        {
            "messages": [{"role": "user", "content": request.message}],
            "conversation_history": history[:-1] if len(history) > 1 else [],
            "session_id": session_id,
        }
    )
    
    response_message = result.get("response", "I apologize, but I couldn't process your request.")
    intent = result.get("intent")
    sources = result.get("sources")
    
    memory.add_message(
        session_id=session_id, 
        role="assistant", 
        content=response_message,
        intent=intent
    )
    
    return ChatResponse(
        session_id=session_id,
        message=response_message,
        intent=intent,
        sources=sources
    )