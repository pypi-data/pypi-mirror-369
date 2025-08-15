"""
Cache Manager

Manages LLM response caching with TTL and size limits.
"""

import logging
from typing import Any, Dict, List, Optional

from cachetools import TTLCache

from unrealon_llm.src.dto import ChatMessage, LLMResponse

logger = logging.getLogger(__name__)


class CacheManager:
    """LLM response cache manager"""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.cache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self.enabled = True
    
    def set_enabled(self, enabled: bool):
        """Enable or disable caching"""
        self.enabled = enabled
        if not enabled:
            self.cache.clear()
    
    def generate_cache_key(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float,
        response_format: Optional[str]
    ) -> str:
        """Generate cache key for request"""
        messages_hash = hash(tuple((msg.role.value, msg.content) for msg in messages))
        return f"{model}_{messages_hash}_{temperature}_{response_format}"
    
    def get(self, cache_key: str) -> Optional[LLMResponse]:
        """Get cached response"""
        if not self.enabled:
            return None
        
        return self.cache.get(cache_key)
    
    def store(self, cache_key: str, response: LLMResponse):
        """Store response in cache"""
        if not self.enabled:
            return
        
        self.cache[cache_key] = response
    
    def clear(self):
        """Clear all cached responses"""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "enabled": self.enabled,
            "cache_size": len(self.cache),
            "max_size": self.cache.maxsize,
            "ttl_seconds": self.cache.ttl if hasattr(self.cache, 'ttl') else 0,
            "cache_info": self.cache.currsize if hasattr(self.cache, 'currsize') else len(self.cache)
        }
