from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.memory.manager import get_memory
from app.agents.graph import get_agent_graph


async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    memory = get_memory()
    
    memory.add_message(session_id=request.session_id, role="user", content=request.message)
    
    history = memory.get_history_as_dict(request.session_id)
    
    agent_graph = get_agent_graph()
    result = await agent_graph.ainvoke(
        {
            "messages": [{"role": "user", "content": request.message}],
            "conversation_history": history[:-1] if len(history) > 1 else [],
            "session_id": request.session_id,
        }
    )
    
    response_message = result.get("response", "I apologize, but I couldn't process your request.")
    intent = result.get("intent")
    sources = result.get("sources")
    
    memory.add_message(
        session_id=request.session_id, 
        role="assistant", 
        content=response_message,
        intent=intent
    )
    
    return ChatResponse(
        session_id=request.session_id,
        message=response_message,
        intent=intent,
        sources=sources
    )