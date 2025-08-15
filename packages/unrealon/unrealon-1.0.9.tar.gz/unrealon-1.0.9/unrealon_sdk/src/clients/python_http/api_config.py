from typing import Optional, Union
import os
from threading import Lock

from pydantic import BaseModel, Field


class APIConfig(BaseModel):
    """
    Global API configuration with thread-safe global state management.
    
    Supports both instance-based and global configuration for convenience.
    """
    
    model_config = {"validate_assignment": True}

    base_path: str = Field(default="http://localhost:8000", description="API base URL")
    verify: Union[bool, str] = Field(default=True, description="SSL verification")
    access_token: Optional[str] = Field(default=None, description="Bearer token for authentication")

    def get_access_token(self) -> Optional[str]:
        """Get access token, falling back to global config if not set."""
        return self.access_token or _global_config.access_token

    def set_access_token(self, value: str):
        """Set access token for this instance."""
        self.access_token = value

    def get_base_path(self) -> str:
        """Get base path, falling back to global config if needed."""
        return self.base_path or _global_config.base_path


class GlobalAPIConfig:
    """
    Thread-safe global API configuration singleton.
    
    Allows setting API configuration once for all generated API calls.
    """
    
    def __init__(self):
        self._lock = Lock()
        self._access_token: Optional[str] = None
        self._base_path: str = "http://localhost:8000"
        self._verify: Union[bool, str] = True
        
        # Auto-load from environment
        self._load_from_environment()
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Try multiple common environment variable names
        env_token = (
            os.getenv("UNREALON_API_KEY") or
            os.getenv("API_KEY") or 
            os.getenv("BEARER_TOKEN") or
            os.getenv("ACCESS_TOKEN")
        )
        
        if env_token:
            self._access_token = env_token
            
        env_base_url = (
            os.getenv("UNREALON_API_URL") or
            os.getenv("API_BASE_URL") or
            os.getenv("BASE_URL")
        )
        
        if env_base_url:
            self._base_path = env_base_url
    
    @property
    def access_token(self) -> Optional[str]:
        """Thread-safe access to global access token."""
        with self._lock:
            return self._access_token
    
    @access_token.setter
    def access_token(self, value: str):
        """Thread-safe setting of global access token."""
        with self._lock:
            self._access_token = value
    
    @property
    def base_path(self) -> str:
        """Thread-safe access to global base path."""
        with self._lock:
            return self._base_path
    
    @base_path.setter
    def base_path(self, value: str):
        """Thread-safe setting of global base path."""
        with self._lock:
            self._base_path = value
    
    @property
    def verify(self) -> Union[bool, str]:
        """Thread-safe access to global verify setting."""
        with self._lock:
            return self._verify
    
    @verify.setter
    def verify(self, value: Union[bool, str]):
        """Thread-safe setting of global verify setting."""
        with self._lock:
            self._verify = value
    
    def configure(self, 
                  access_token: Optional[str] = None,
                  base_path: Optional[str] = None,
                  verify: Optional[Union[bool, str]] = None):
        """
        Configure global API settings in one call.
        
        Args:
            access_token: Bearer token for authentication
            base_path: API base URL
            verify: SSL verification setting
        """
        with self._lock:
            if access_token is not None:
                self._access_token = access_token
            if base_path is not None:
                self._base_path = base_path
            if verify is not None:
                self._verify = verify
    
    def get_config(self) -> APIConfig:
        """
        Get current global configuration as APIConfig instance.
        
        Returns:
            APIConfig: Current global configuration
        """
        with self._lock:
            return APIConfig(
                base_path=self._base_path,
                verify=self._verify,
                access_token=self._access_token
            )
    
    def reset(self):
        """Reset to default configuration."""
        with self._lock:
            self._access_token = None
            self._base_path = "http://localhost:8000"
            self._verify = True
            self._load_from_environment()


# Global configuration singleton
_global_config = GlobalAPIConfig()


def set_global_api_key(api_key: str):
    """
    Convenience function to set global API key.
    
    Args:
        api_key: Bearer token for authentication
        
    Example:
        from unrealon_sdk.clients.python_http.api_config import set_global_api_key
        set_global_api_key("up_dev_your_api_key_here")
    """
    _global_config.access_token = api_key


def set_global_base_url(base_url: str):
    """
    Convenience function to set global base URL.
    
    Args:
        base_url: API base URL
        
    Example:
        from unrealon_sdk.clients.python_http.api_config import set_global_base_url
        set_global_base_url("https://api.example.com")
    """
    _global_config.base_path = base_url


def configure_global_api(api_key: str, base_url: Optional[str] = None, verify: Optional[Union[bool, str]] = None):
    """
    Convenience function to configure global API settings.
    
    Args:
        api_key: Bearer token for authentication
        base_url: API base URL (optional)
        verify: SSL verification setting (optional)
        
    Example:
        from unrealon_sdk.clients.python_http.api_config import configure_global_api
        configure_global_api("up_dev_your_api_key_here", "https://api.example.com")
    """
    _global_config.configure(access_token=api_key, base_path=base_url, verify=verify)


def get_global_config() -> APIConfig:
    """
    Get current global API configuration.
    
    Returns:
        APIConfig: Current global configuration
        
    Example:
        from unrealon_sdk.clients.python_http.api_config import get_global_config
        config = get_global_config()
        print(f"Current API key: {config.get_access_token()}")
    """
    return _global_config.get_config()


class HTTPException(Exception):
    """HTTP exception for API errors."""
    
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"{status_code} {message}")

    def __str__(self):
        return f"{self.status_code} {self.message}"


# Auto-configure from environment on import
# This allows zero-configuration usage if environment variables are set
_global_config._load_from_environment()