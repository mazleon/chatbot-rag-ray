import logging
from abc import ABC, abstractmethod
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    def get_model(self) -> BaseChatModel:
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, settings):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
    
    def get_model(self) -> ChatOpenAI:
        logger.info(f"Initializing OpenAI provider with model: {self.model}")
        return ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key,
        )


class OpenRouterProvider(LLMProvider):
    def __init__(self, settings):
        self.api_key = settings.openrouter_api_key or settings.openai_api_key
        self.model = settings.openrouter_model
        self.base_url = settings.openrouter_base_url
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
    
    def get_model(self) -> BaseChatModel:
        logger.info(f"Initializing OpenRouter provider with model: {self.model}")
        
        if "claude" in self.model.lower() or "anthropic" in self.model.lower():
            return ChatAnthropic(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                api_key=self.api_key,
                base_url=self.base_url,
            )
        
        return ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key,
            base_url=self.base_url,
        )


class LLMProviderFactory:
    _providers = {
        "openai": OpenAIProvider,
        "openrouter": OpenRouterProvider,
    }
    
    @classmethod
    def create(cls, provider_name: str, settings) -> LLMProvider:
        provider_class = cls._providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
        return provider_class(settings)


class LLMService:
    def __init__(self):
        settings = get_settings()
        self.provider_name = settings.llm_provider
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
        
        logger.info(f"Initializing LLM service with provider: {self.provider_name}")
        
        provider = LLMProviderFactory.create(self.provider_name, settings)
        self.llm = provider.get_model()
        
        from app.services.langfuse import get_langfuse_service
        self.langfuse = get_langfuse_service()
    
    async def chat(self, message: str, system_prompt: Optional[str] = None, session_id: Optional[str] = None) -> str:
        from langchain_core.messages import HumanMessage, SystemMessage
        
        logger.debug(f"Chat request - message length: {len(message)}")
        
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=message))
        
        try:
            logger.info(f"Calling LLM with provider: {self.provider_name}")
            response = self.llm.invoke(messages)
            response_content = response.content if hasattr(response, "content") else str(response)
            logger.info(f"LLM response received - length: {len(response_content)}")
            
            if self.langfuse and self.langfuse.is_enabled() and session_id:
                self.langfuse.trace_generation(
                    session_id=session_id,
                    user_message=message,
                    model=self.provider_name,
                    prompt=system_prompt or "",
                    response=response_content,
                )
            
            return response_content
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}", exc_info=True)
            from app.utils.exceptions import LLMGenerationError
            raise LLMGenerationError(str(e))


_llm_service = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        try:
            logger.info("Initializing LLM service")
            _llm_service = LLMService()
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}", exc_info=True)
            raise
    return _llm_service
