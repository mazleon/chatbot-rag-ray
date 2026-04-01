from enum import Enum


class IntentType(str, Enum):
    POLICY_INFO = "policy_info"
    BENEFITS = "benefits"
    ELIGIBILITY = "eligibility"
    CLAIMS = "claims"
    PREMIUM_CALC = "premium_calc"
    GENERAL = "general"
    GREETING = "greeting"


API_TITLE = "Life Insurance AI Support Agent"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI-powered customer support for life insurance"

MAX_MESSAGE_LENGTH = 2000
MAX_CONTEXT_LENGTH = 4096
MAX_RETRIES = 3

DEFAULT_TIMEOUT = 30
LONG_TIMEOUT = 120

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

ERROR_LLM_UNAVAILABLE = "AI service is temporarily unavailable"
ERROR_INVALID_REQUEST = "Invalid request parameters"
ERROR_SESSION_NOT_FOUND = "Session not found"
ERROR_VECTORSTORE_EMPTY = "Knowledge base is empty"