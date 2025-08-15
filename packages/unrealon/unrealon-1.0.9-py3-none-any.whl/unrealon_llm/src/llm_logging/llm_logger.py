"""
LLM Logger - Specialized logging for AI operations

Wraps the SDK DevelopmentLogger with LLM-specific convenience methods.
Provides structured logging for AI operations, cost tracking, and performance monitoring.
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from unrealon_sdk.src.enterprise.logging.development import (
    DevelopmentLogger, 
    initialize_development_logger,
    get_development_logger
)
from unrealon_sdk.src.dto.logging import SDKEventType, SDKSeverity, SDKContext

from .llm_events import LLMEventType, LLMContext


class LLMLogger:
    """
    Specialized logger for LLM operations.
    
    Wraps the SDK DevelopmentLogger with convenience methods for:
    - LLM request/response logging
    - Cost tracking and budget monitoring
    - HTML analysis operations
    - Token counting and optimization
    - Performance metrics
    """
    
    def __init__(self, dev_logger: Optional[DevelopmentLogger] = None):
        """Initialize LLM logger with optional development logger."""
        self._dev_logger = dev_logger or get_development_logger()
        if not self._dev_logger:
            raise RuntimeError(
                "No development logger available. Call initialize_llm_logger() first."
            )
    
    # LLM Request Logging
    def log_llm_request_start(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log start of LLM request."""
        context = SDKContext(
            component_name="LLMClient",
            layer_name="UnrealOn_LLM",
            correlation_id=request_id,
        )
        
        # Add LLM-specific details
        llm_details = details or {}
        llm_details.update({
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
        })
        
        self._dev_logger.log_info(
            LLMEventType.LLM_REQUEST_STARTED,
            f"Starting LLM request to {provider}/{model} ({prompt_tokens} tokens)",
            context=context,
            details=details,
        )
    
    def log_llm_request_completed(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        duration_ms: float,
        request_id: Optional[str] = None,
        cached: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log successful LLM request completion."""
        context = LLMContext()
        
        message = f"LLM request completed: {provider}/{model}"
        if cached:
            message += " (cached)"
        message += f" - {prompt_tokens + completion_tokens} tokens, ${cost_usd:.4f}"
        
        event_type = LLMEventType.LLM_REQUEST_CACHED if cached else LLMEventType.LLM_REQUEST_COMPLETED
        
        self._dev_logger.log_info(
            event_type,
            message,
            context=context,
            details=details,
            duration_ms=duration_ms,
        )
    
    def log_llm_response_received(
        self,
        provider: str,
        model: str,
        completion_tokens: int,
        total_tokens: int,
        cost_usd: float,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log LLM response received."""
        context = LLMContext()
        
        # Add response details
        llm_details = details or {}
        llm_details.update({
            "provider": provider,
            "model": model,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost_usd,
        })
        
        self._dev_logger.log_info(
            LLMEventType.LLM_REQUEST_COMPLETED,
            f"LLM response received: {provider}/{model} - {total_tokens} tokens, ${cost_usd:.4f}",
            context=context,
            details=llm_details,
        )
    
    def log_llm_request_failed(
        self,
        provider: str,
        model: str,
        error_message: str,
        request_id: Optional[str] = None,
        retry_count: Optional[int] = None,
        exception: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log failed LLM request."""
        context = LLMContext()
        
        message = f"LLM request failed: {provider}/{model}"
        if retry_count is not None:
            message += f" (retry {retry_count})"
        
        self._dev_logger.log_error(
            LLMEventType.LLM_REQUEST_FAILED,
            message,
            context=context,
            details=details,
            error_message=error_message,
            exception=exception,
        )
    
    # Cost Tracking
    def log_cost_tracking(
        self,
        operation_cost_usd: float,
        daily_total_usd: float,
        daily_limit_usd: float,
        model: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log cost tracking information."""
        context = LLMContext()
        
        utilization = (daily_total_usd / daily_limit_usd) * 100
        
        if utilization >= 90:
            severity = SDKSeverity.WARNING
            event_type = LLMEventType.COST_LIMIT_WARNING
            message = f"Cost limit warning: ${daily_total_usd:.4f}/${daily_limit_usd:.2f} ({utilization:.1f}%)"
        elif utilization >= 100:
            severity = SDKSeverity.ERROR
            event_type = LLMEventType.COST_LIMIT_EXCEEDED
            message = f"Cost limit exceeded: ${daily_total_usd:.4f}/${daily_limit_usd:.2f}"
        else:
            severity = SDKSeverity.DEBUG
            event_type = LLMEventType.COST_CALCULATED
            message = f"Cost tracked: +${operation_cost_usd:.4f} (daily: ${daily_total_usd:.4f}/${daily_limit_usd:.2f})"
        
        self._dev_logger._log_event(
            event_type=event_type,
            message=message,
            severity=severity,
            context=context,
            details=details,
        )
    
    # HTML Analysis Logging
    def log_html_analysis_start(
        self,
        html_size_bytes: int,
        target_elements: List[str],
        analysis_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log start of HTML analysis."""
        context = SDKContext(
            correlation_id=analysis_id,
            component_name="HTMLAnalyzer",
            layer_name="UnrealOn_LLM"
        )
        
        # Add LLM-specific details to the details dict
        llm_details = details or {}
        llm_details.update({
            "html_size_bytes": html_size_bytes,
            "target_elements": target_elements,
        })
        
        self._dev_logger.log_info(
            LLMEventType.HTML_ANALYSIS_STARTED,
            f"Starting HTML analysis: {html_size_bytes:,} bytes, targeting {len(target_elements)} elements",
            context=context,
            details=llm_details,
        )
    
    def log_html_analysis_completed(
        self,
        selectors_generated: int,
        confidence_score: float,
        analysis_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log successful HTML analysis completion."""
        context = LLMContext()
        
        self._dev_logger.log_info(
            LLMEventType.HTML_ANALYSIS_COMPLETED,
            f"HTML analysis completed: {selectors_generated} selectors, {confidence_score:.2f} confidence",
            context=context,
            details=details,
            duration_ms=duration_ms,
        )
    
    def log_html_cleaning(
        self,
        original_size_bytes: int,
        cleaned_size_bytes: int,
        optimization_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log HTML cleaning and optimization."""
        reduction_pct = ((original_size_bytes - cleaned_size_bytes) / original_size_bytes) * 100
        
        context = LLMContext()
        
        self._dev_logger.log_debug(
            LLMEventType.HTML_CLEANING_APPLIED,
            f"HTML cleaned: {original_size_bytes:,} → {cleaned_size_bytes:,} bytes ({reduction_pct:.1f}% reduction)",
            context=context,
            details={
                "html_size_bytes": original_size_bytes,
                "cleaned_html_size_bytes": cleaned_size_bytes,
                "original_size_bytes": original_size_bytes,
                "cleaned_size_bytes": cleaned_size_bytes,
                "reduction_percentage": reduction_pct,
                "optimization_type": optimization_type,
                "optimization_applied": optimization_type,
                **(details or {})
            }
        )
    
    def log_html_analysis_failed(
        self,
        error_message: str,
        analysis_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log failed HTML analysis."""
        context = SDKContext(
            correlation_id=analysis_id,
            component_name="HTMLAnalyzer",
            layer_name="UnrealOn_LLM"
        )
        
        self._dev_logger.log_error(
            LLMEventType.LLM_REQUEST_FAILED,
            f"HTML analysis failed: {error_message}",
            context=context,
            details=details,
            error_message=error_message,
        )
    
    # Token Management
    def log_token_counting(
        self,
        text_length: int,
        token_count: int,
        model: str,
        optimization_applied: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log token counting operations."""
        context = LLMContext()
        
        event_type = LLMEventType.TOKEN_OPTIMIZATION_APPLIED if optimization_applied else LLMEventType.TOKENS_COUNTED
        message = f"Tokens counted: {text_length:,} chars → {token_count:,} tokens ({model})"
        if optimization_applied:
            message += " [optimized]"
        
        self._dev_logger.log_debug(
            event_type,
            message,
            context=context,
            details=details,
        )
    
    # Translation Logging
    def log_translation(
        self,
        source_lang: str,
        target_lang: str,
        text_length: int,
        success: bool = True,
        duration_ms: Optional[float] = None,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log translation operations."""
        context = LLMContext()
        
        if success:
            self._dev_logger.log_info(
                LLMEventType.TRANSLATION_COMPLETED,
                f"Translation completed: {source_lang} → {target_lang} ({text_length:,} chars)",
                context=context,
                details=details,
                duration_ms=duration_ms,
            )
        else:
            self._dev_logger.log_error(
                LLMEventType.TRANSLATION_COMPLETED,
                f"Translation failed: {source_lang} → {target_lang}",
                context=context,
                details=details,
                error_message=error_message,
            )
    
    # Performance Metrics
    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        threshold: Optional[float] = None,
        context: Optional[LLMContext] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log performance metrics with LLM context."""
        # Use the underlying dev logger's performance metric method
        self._dev_logger.log_performance_metric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            threshold=threshold,
            context=context,
        )
    
    # Cache Operations
    def log_cache_operation(
        self,
        operation: str,  # hit, miss, store
        cache_key: str,
        hit_rate: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log cache operations."""
        context = LLMContext()
        
        event_type_map = {
            "hit": LLMEventType.CACHE_HIT,
            "miss": LLMEventType.CACHE_MISS,
            "store": LLMEventType.RESPONSE_CACHED,
        }
        
        event_type = event_type_map.get(operation, LLMEventType.CACHE_HIT)
        
        self._dev_logger.log_debug(
            event_type,
            f"Cache {operation}: {cache_key[:50]}{'...' if len(cache_key) > 50 else ''}",
            context=context,
            details=details,
        )
    
    # Layer and Component Context (delegated to dev logger)
    def set_layer_context(self, layer_name: str) -> None:
        """Set current layer context."""
        self._dev_logger.set_layer_context(layer_name)
    
    def set_component_context(self, component_name: str) -> None:
        """Set current component context."""  
        self._dev_logger.set_component_context(component_name)
    
    def start_operation(self, operation_id: str, description: str) -> None:
        """Start tracking a long-running operation."""
        self._dev_logger.start_operation(operation_id, description)
    
    def complete_operation(self, operation_id: str, description: str, success: bool = True) -> None:
        """Complete a tracked operation."""
        self._dev_logger.complete_operation(operation_id, description, success)


# Global LLM logger instance
_llm_logger: Optional[LLMLogger] = None


def initialize_llm_logger(
    session_id: Optional[str] = None,
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_websocket: bool = True,
) -> LLMLogger:
    """
    Initialize global LLM logger.
    
    Creates a development logger and wraps it with LLM-specific functionality.
    """
    global _llm_logger
    
    # Map string log levels to SDK severity
    level_map = {
        "TRACE": SDKSeverity.TRACE,
        "DEBUG": SDKSeverity.DEBUG,
        "INFO": SDKSeverity.INFO,
        "WARNING": SDKSeverity.WARNING,
        "ERROR": SDKSeverity.ERROR,
        "CRITICAL": SDKSeverity.CRITICAL,
    }
    
    sdk_level = level_map.get(log_level.upper(), SDKSeverity.INFO)
    
    # Initialize or get existing dev logger
    dev_logger = get_development_logger()
    if not dev_logger:
        dev_logger = initialize_development_logger(
            session_id=session_id,
            log_level=sdk_level,
            enable_console=enable_console,
            enable_websocket=enable_websocket,
        )
    
    # Set LLM layer context
    dev_logger.set_layer_context("UnrealOn_LLM")
    
    _llm_logger = LLMLogger(dev_logger)
    
    # Log initialization
    _llm_logger._dev_logger.log_info(
        LLMEventType.LLM_CLIENT_INITIALIZED,
        "LLM Logger initialized with SDK integration",
        context=LLMContext(),
    )
    
    return _llm_logger


def get_llm_logger() -> Optional[LLMLogger]:
    """Get global LLM logger instance."""
    return _llm_logger
