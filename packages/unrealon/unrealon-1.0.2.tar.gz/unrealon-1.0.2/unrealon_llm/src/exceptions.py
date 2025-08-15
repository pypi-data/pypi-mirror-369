"""
UnrealOn LLM Exceptions

Custom exception classes for UnrealOn LLM platform with detailed error information.
All exceptions follow KISS methodology with clear error messages and context.
"""

from typing import Any, Dict, Optional


class LLMError(Exception):
    """Base exception for all LLM operations"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
    
    def __str__(self) -> str:
        error_info = f"LLMError: {self.message}"
        if self.error_code:
            error_info += f" (Code: {self.error_code})"
        return error_info


class APIError(LLMError):
    """Base class for API-related errors"""
    pass


class OpenRouterAPIError(APIError):
    """OpenRouter API specific errors"""
    pass


class OpenAIAPIError(APIError):
    """OpenAI API specific errors"""
    pass


class AnthropicAPIError(APIError):
    """Anthropic API specific errors"""
    pass


class RateLimitError(APIError):
    """API rate limit exceeded"""
    
    def __init__(
        self, 
        message: str = "API rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class APIQuotaExceededError(APIError):
    """API quota exceeded"""
    pass


class ModelUnavailableError(APIError):
    """Requested model is not available"""
    
    def __init__(
        self, 
        model_name: str,
        available_models: Optional[list] = None,
        **kwargs
    ):
        message = f"Model '{model_name}' is not available"
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.available_models = available_models or []


class NetworkError(APIError):
    """Network connectivity issues"""
    pass


class AuthenticationError(APIError):
    """API authentication failed"""
    pass


class CostLimitExceededError(LLMError):
    """Cost limit exceeded"""
    
    def __init__(
        self, 
        current_cost: float,
        limit: float,
        **kwargs
    ):
        message = f"Cost limit exceeded: ${current_cost:.4f} > ${limit:.4f}"
        super().__init__(message, **kwargs)
        self.current_cost = current_cost
        self.limit = limit


class TokenLimitExceededError(LLMError):
    """Token limit exceeded"""
    
    def __init__(
        self, 
        token_count: int,
        limit: int,
        **kwargs
    ):
        message = f"Token limit exceeded: {token_count} > {limit}"
        super().__init__(message, **kwargs)
        self.token_count = token_count
        self.limit = limit


class ValidationError(LLMError):
    """Data validation errors"""
    pass


class HTMLParsingError(LLMError):
    """HTML parsing and analysis errors"""
    pass


class HTMLTooLargeError(HTMLParsingError):
    """HTML content too large for processing"""
    
    def __init__(
        self, 
        html_size: int,
        max_size: int,
        **kwargs
    ):
        message = f"HTML too large: {html_size} bytes > {max_size} bytes limit"
        super().__init__(message, **kwargs)
        self.html_size = html_size
        self.max_size = max_size


class PatternDetectionError(HTMLParsingError):
    """Pattern detection failed"""
    pass


class SelectorGenerationError(HTMLParsingError):
    """Selector generation failed"""
    pass


class SelectorValidationError(HTMLParsingError):
    """Selector validation failed"""
    
    def __init__(
        self, 
        selector: str,
        validation_message: str,
        **kwargs
    ):
        message = f"Selector validation failed: '{selector}' - {validation_message}"
        super().__init__(message, **kwargs)
        self.selector = selector
        self.validation_message = validation_message


class TranslationError(LLMError):
    """Translation operation errors"""
    pass


class LanguageDetectionError(TranslationError):
    """Language detection failed"""
    pass


class TranslationQualityError(TranslationError):
    """Translation quality below threshold"""
    
    def __init__(
        self, 
        quality_score: float,
        threshold: float,
        **kwargs
    ):
        message = f"Translation quality too low: {quality_score:.2f} < {threshold:.2f}"
        super().__init__(message, **kwargs)
        self.quality_score = quality_score
        self.threshold = threshold


class SchemaGenerationError(LLMError):
    """Schema generation errors"""
    pass


class TypeInferenceError(SchemaGenerationError):
    """Type inference failed"""
    pass


class CodeGenerationError(SchemaGenerationError):
    """Generated code is invalid"""
    
    def __init__(
        self, 
        code_type: str,
        syntax_error: str,
        **kwargs
    ):
        message = f"{code_type} code generation failed: {syntax_error}"
        super().__init__(message, **kwargs)
        self.code_type = code_type
        self.syntax_error = syntax_error


class CacheError(LLMError):
    """Cache operation errors"""
    pass


class CacheCorruptionError(CacheError):
    """Cache data is corrupted"""
    pass


class ConfigurationError(LLMError):
    """Configuration errors"""
    pass


class MissingAPIKeyError(ConfigurationError):
    """API key is missing"""
    
    def __init__(
        self, 
        provider: str,
        **kwargs
    ):
        message = f"API key missing for provider: {provider}"
        super().__init__(message, **kwargs)
        self.provider = provider


class InvalidConfigurationError(ConfigurationError):
    """Configuration is invalid"""
    pass


class TestingError(LLMError):
    """Testing infrastructure errors"""
    pass


class MockSetupError(TestingError):
    """Mock setup failed"""
    pass


class CostSimulationError(TestingError):
    """Cost simulation failed"""
    pass


class ResponseParsingError(LLMError):
    """Failed to parse LLM response"""
    
    def __init__(
        self, 
        response_content: str,
        expected_format: str,
        **kwargs
    ):
        message = f"Failed to parse response as {expected_format}"
        super().__init__(message, **kwargs)
        self.response_content = response_content[:200] + "..." if len(response_content) > 200 else response_content
        self.expected_format = expected_format


class ProcessingPipelineError(LLMError):
    """Processing pipeline errors"""
    
    def __init__(
        self, 
        stage: str,
        stage_error: Exception,
        **kwargs
    ):
        message = f"Pipeline failed at stage '{stage}': {str(stage_error)}"
        super().__init__(message, **kwargs)
        self.stage = stage
        self.stage_error = stage_error


class RetryExhaustedError(LLMError):
    """All retry attempts exhausted"""
    
    def __init__(
        self, 
        operation: str,
        attempts: int,
        last_error: Exception,
        **kwargs
    ):
        message = f"Operation '{operation}' failed after {attempts} attempts"
        super().__init__(message, **kwargs)
        self.operation = operation
        self.attempts = attempts
        self.last_error = last_error


# Convenience functions for common error patterns
def raise_if_cost_exceeded(current_cost: float, limit: float) -> None:
    """Raise CostLimitExceededError if cost exceeds limit"""
    if current_cost > limit:
        raise CostLimitExceededError(current_cost, limit)


def raise_if_tokens_exceeded(token_count: int, limit: int) -> None:
    """Raise TokenLimitExceededError if tokens exceed limit"""
    if token_count > limit:
        raise TokenLimitExceededError(token_count, limit)


def raise_if_html_too_large(html_size: int, max_size: int) -> None:
    """Raise HTMLTooLargeError if HTML exceeds size limit"""
    if html_size > max_size:
        raise HTMLTooLargeError(html_size, max_size)


def wrap_api_error(provider: str, original_error: Exception) -> APIError:
    """Wrap provider-specific API errors"""
    error_message = str(original_error)
    
    if provider.lower() == "openrouter":
        return OpenRouterAPIError(error_message, context={"original_error": original_error})
    elif provider.lower() == "openai":
        return OpenAIAPIError(error_message, context={"original_error": original_error})
    elif provider.lower() == "anthropic":
        return AnthropicAPIError(error_message, context={"original_error": original_error})
    else:
        return APIError(error_message, context={"provider": provider, "original_error": original_error})


# Error code constants
class ErrorCodes:
    """Standard error codes for LLM operations"""
    
    # API errors
    RATE_LIMIT = "RATE_LIMIT"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    AUTHENTICATION_FAILED = "AUTH_FAILED"
    NETWORK_ERROR = "NETWORK_ERROR"
    
    # Cost errors
    COST_LIMIT_EXCEEDED = "COST_LIMIT"
    TOKEN_LIMIT_EXCEEDED = "TOKEN_LIMIT"
    
    # HTML errors
    HTML_TOO_LARGE = "HTML_TOO_LARGE"
    PATTERN_DETECTION_FAILED = "PATTERN_FAILED"
    SELECTOR_GENERATION_FAILED = "SELECTOR_FAILED"
    SELECTOR_VALIDATION_FAILED = "SELECTOR_INVALID"
    
    # Translation errors
    LANGUAGE_DETECTION_FAILED = "LANG_DETECT_FAILED"
    TRANSLATION_QUALITY_LOW = "TRANSLATION_LOW_QUALITY"
    
    # Schema errors
    TYPE_INFERENCE_FAILED = "TYPE_INFERENCE_FAILED"
    CODE_GENERATION_FAILED = "CODE_GEN_FAILED"
    
    # Cache errors
    CACHE_CORRUPTED = "CACHE_CORRUPTED"
    
    # Config errors
    MISSING_API_KEY = "MISSING_API_KEY"
    INVALID_CONFIG = "INVALID_CONFIG"
    
    # Processing errors
    PIPELINE_FAILED = "PIPELINE_FAILED"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"
    RESPONSE_PARSING_FAILED = "RESPONSE_PARSE_FAILED"
