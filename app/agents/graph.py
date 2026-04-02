import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    messages: List[Dict[str, str]] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    session_id: str = ""
    intent: Optional[str] = None
    retrieved_docs: List[Dict[str, Any]] = field(default_factory=list)
    response: Optional[str] = None
    error: Optional[str] = None


async def classify_node(state: AgentState) -> AgentState:
    last_message = state.messages[-1]["content"].lower()
    logger.debug(f"Classifying message: {last_message[:50]}...")
    
    keywords = {
        "claims": ["file claim", "claim", "process", "documents", "submit", "death benefit"],
        "premium": ["premium", "cost", "price", "pay", "monthly", "yearly", "expensive", "cheap"],
        "eligibility": ["eligible", "qualify", "who can", "can i get", "requirement", "age limit"],
        "benefits": ["benefit", "payout", "receive", "coverage amount"],
        "policy_info": ["policy", "term", "coverage", "plan", "type", "insurance", "life insurance"],
        "document_query": ["my document", "my file", "uploaded", "what does it say", "according to"],
        "summarize": ["summarize", "summary", "summarise", "recap", "what did we discuss", "review"],
        "personal_info": ["my name", "what is my name", "who am i", "do you know me", "remember me"],
    }
    
    for intent, words in keywords.items():
        if any(word in last_message for word in words):
            state.intent = intent
            break
    else:
        state.intent = "general"
    
    logger.info(f"Classified intent: {state.intent}")
    return state


async def retrieve_node(state: AgentState) -> AgentState:
    should_retrieve = state.intent in ["policy_info", "benefits", "eligibility", "claims", "premium", "document_query"] or state.intent == "summarize"
    
    if not should_retrieve and state.conversation_history:
        should_retrieve = True
    
    if should_retrieve:
        from app.services.rag import get_rag_service
        rag_service = get_rag_service()
        
        if rag_service and rag_service.vectorstore is not None:
            last_message = state.messages[-1]["content"]
            logger.info(f"Retrieving documents for intent: {state.intent}")
            try:
                docs = await rag_service.retrieve(last_message, session_id=state.session_id)
                state.retrieved_docs = docs
                logger.info(f"Retrieved {len(docs)} documents")
            except Exception as e:
                logger.error(f"RAG retrieval failed: {e}", exc_info=True)
                state.error = f"RAG error: {str(e)}"
        else:
            logger.warning("RAG service or vectorstore not available")
    else:
        logger.debug(f"Skipping retrieval for intent: {state.intent}")
    
    return state


async def generate_node(state: AgentState) -> AgentState:
    from app.services.llm import get_llm_service
    
    llm_service = get_llm_service()
    last_message = state.messages[-1]["content"]
    
    logger.info("Generating response")
    
    context = ""
    if state.retrieved_docs:
        context = "\n\n".join([
            f"Reference {i+1}: {doc.get('text', '')}"
            for i, doc in enumerate(state.retrieved_docs)
        ])
        logger.debug(f"Using {len(state.retrieved_docs)} documents as context")
    
    history_text = ""
    if state.conversation_history:
        history_lines = []
        for msg in state.conversation_history:
            role_label = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            if content:
                history_lines.append(f"{role_label}: {content}")
        if history_lines:
            history_text = "Previous conversation:\n" + "\n".join(history_lines) + "\n\n"
    
    is_summarize = state.intent == "summarize" or "summarize" in last_message or "summary" in last_message
    is_personal_info = state.intent == "personal_info" or "my name" in last_message or "who am i" in last_message or "do you know me" in last_message
    
    name_from_history = ""
    extracted_from_history = False
    if state.conversation_history:
        logger.info(f"Checking conversation history for name. History length: {len(state.conversation_history)}")
        for i, msg in enumerate(state.conversation_history):
            content = msg.get("content", "").lower()
            logger.info(f"Message {i}: {msg.get('content', '')[:50]}")
            if "my name is" in content:
                parts = msg.get("content", "").split("my name is")
                if len(parts) > 1:
                    name_from_history = parts[1].strip().split()[0].rstrip("!.,")
                    extracted_from_history = True
                    break
            elif "i'm " in content or "i am " in content:
                parts = msg.get("content", "").split()
                for j, w in enumerate(parts):
                    if w.lower() in ["i'm", "i am"]:
                        if j + 1 < len(parts):
                            name_from_history = parts[j + 1].rstrip("!.,")
                            extracted_from_history = True
                            break
                if extracted_from_history:
                    break
        
        if extracted_from_history:
            logger.info(f"Extracted name from history: {name_from_history}")
    
    personal_info_instruction = ""
    if is_personal_info:
        if name_from_history:
            personal_info_instruction = f"- The user's name is {name_from_history}. Tell them their name!"
        else:
            personal_info_instruction = "- The user is asking about their personal information but hasn't told us their name yet. Ask them what their name is."
    
    system_prompt = f"""You are a helpful life insurance support agent.
Your role is to help users understand life insurance products, benefits, 
eligibility criteria, claims processes, and premium calculations.

IMPORTANT - Always use the provided context:
- If context is provided (marked as "Context:"), you MUST answer based on that document
- Do NOT say "I don't have access to your document" if context is provided
- Quote or reference specific parts of the document when answering
- The context contains information from user's uploaded documents

Guidelines:
- Be helpful, accurate, and empathetic
- Use information from provided context when available
- If you don't know something, say so honestly
- Don't provide specific premium quotes (redirect to agent)
- Always recommend professional advice for complex decisions
- Remember relevant details from the conversation history
{"- When asked to summarize, provide a clear and concise summary of the conversation below" if is_summarize else ""}
{personal_info_instruction if personal_info_instruction else ""}

{history_text}{'Context: ' + context if context else ''}

User: {last_message}"""
    
    try:
        response = await llm_service.chat(
            message=last_message,
            system_prompt=system_prompt,
            session_id=state.session_id
        )
        state.response = response
        logger.info("Response generated successfully")
        
        from app.services.langfuse import get_langfuse_service
        langfuse = get_langfuse_service()
        if langfuse and langfuse.is_enabled() and state.session_id:
            langfuse.trace_agent_flow(
                session_id=state.session_id,
                user_message=last_message,
                intent=state.intent or "general",
                response=response,
                conversation_history=state.conversation_history,
            )
    except Exception as e:
        logger.error(f"LLM generation failed: {e}", exc_info=True)
        state.response = "I apologize, but I'm having trouble generating a response right now. Please try again later."
        state.error = str(e)
    
    return state


def create_agent_graph() -> StateGraph:
    logger.info("Creating agent graph")
    graph = StateGraph(AgentState)
    
    graph.add_node("classify", classify_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    
    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    
    logger.info("Agent graph created successfully")
    return graph.compile()


_agent_graph = None


def get_agent_graph() -> StateGraph:
    global _agent_graph
    if _agent_graph is None:
        logger.info("Initializing agent graph")
        _agent_graph = create_agent_graph()
    return _agent_graph
