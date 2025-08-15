"""
Authentication-related Data Transfer Objects

Custom DTO models for enterprise authentication system functionality.
These models provide type-safe authentication state and security tracking.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class AuthenticationStatus(str, Enum):
    """Authentication status states."""
    
    UNAUTHENTICATED = "unauthenticated"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    EXPIRED = "expired"
    FAILED = "failed"
    LOCKED = "locked"


class SecurityEventType(str, Enum):
    """Security event types for monitoring."""
    
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    TOKEN_REFRESH = "token_refresh"
    API_KEY_VALIDATION = "api_key_validation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SECURITY_BREACH = "security_breach"
    ACCOUNT_LOCKED = "account_locked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class AuthenticationContext(BaseModel):
    """
    Type-safe authentication context.
    
    Tracks current authentication state and security metrics
    using Pydantic validation instead of Dict[str, Any].
    """
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    # Authentication state
    status: AuthenticationStatus = Field(default=AuthenticationStatus.UNAUTHENTICATED)
    api_key: Optional[str] = Field(None, description="Masked API key for logging")
    access_token: Optional[str] = Field(None, description="Current access token")
    
    # Session information
    session_id: Optional[str] = Field(None, description="Authentication session ID")
    parser_id: Optional[str] = Field(None, description="Registered parser ID")
    authenticated_at: Optional[datetime] = Field(None, description="Authentication timestamp")
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")
    
    # Security metrics
    login_attempts: int = Field(default=0, description="Number of login attempts")
    failed_attempts: int = Field(default=0, description="Number of failed attempts")
    last_login_attempt: Optional[datetime] = Field(None, description="Last login attempt time")
    rate_limit_reset_time: Optional[datetime] = Field(None, description="Rate limit reset time")
    
    # Environment context
    environment: str = Field(default="dev", description="API environment (dev/prod)")
    client_info: Dict[str, str] = Field(default_factory=dict, description="Client metadata")


class SecurityEvent(BaseModel):
    """Security event for audit trails and monitoring."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    event_id: str = Field(..., description="Unique event identifier")
    event_type: SecurityEventType = Field(..., description="Type of security event")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: Optional[str] = Field(None, description="Associated session ID")
    api_key_hash: Optional[str] = Field(None, description="Hashed API key for privacy")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    success: bool = Field(..., description="Whether the operation succeeded")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event data")


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    max_attempts: int = Field(default=5, description="Maximum attempts per window")
    window_seconds: int = Field(default=300, description="Rate limit window in seconds")
    lockout_duration_seconds: int = Field(default=900, description="Lockout duration")
    progressive_delay: bool = Field(default=True, description="Enable progressive delay")


__all__ = [
    # Enums
    "AuthenticationStatus",
    "SecurityEventType",
    
    # Models
    "AuthenticationContext",
    "SecurityEvent", 
    "RateLimitConfig",
]
