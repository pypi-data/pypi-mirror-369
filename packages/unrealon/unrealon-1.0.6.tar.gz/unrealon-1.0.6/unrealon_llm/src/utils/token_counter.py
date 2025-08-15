"""
Token Counting Utilities

Pure token counting with tiktoken - no hardcoded models.
Works with ModelsCache for model information.
"""

import re
from typing import Dict, List, Optional

import tiktoken

from unrealon_llm.src.dto import ChatMessage
from unrealon_llm.src.exceptions import ValidationError


class TokenCounter:
    """Pure token counting utility - no model knowledge"""
    
    def __init__(self):
        """Initialize token counter"""
        # Cache for encoding objects
        self._encoding_cache: Dict[str, any] = {}
        
        # Universal encoding for all models
        self._universal_encoding = "cl100k_base"
        
        # Language ratios for character-based estimation
        self._language_ratios = {
            "english": 0.25,      # ~4 chars per token
            "korean": 0.33,       # ~3 chars per token  
            "chinese": 0.5,       # ~2 chars per token
            "japanese": 0.4,      # ~2.5 chars per token
            "russian": 0.25,      # ~4 chars per token
            "default": 0.25       # Conservative estimate
        }
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Count tokens in text for specified model
        
        Args:
            text: Text to count tokens for
            model: Model name
            
        Returns:
            Number of tokens
        """
        if not isinstance(text, str):
            raise ValidationError("Text must be a string")
        
        if not text:
            return 0
        
        # Try tiktoken first
        try:
            return self._count_with_tiktoken(text, model)
        except Exception:
            # Fallback to estimation
            return self._estimate_tokens(text)
    
    def count_message_tokens(self, messages: List[ChatMessage], model: str = "gpt-3.5-turbo") -> int:
        """
        Count tokens for chat messages including formatting overhead
        
        Args:
            messages: List of chat messages
            model: Model name
            
        Returns:
            Total tokens including overhead
        """
        if not messages:
            return 0
        
        total_tokens = 0
        
        # Count tokens for each message
        for message in messages:
            # Content tokens
            total_tokens += self.count_tokens(message.content, model)
            
            # Role tokens
            total_tokens += self.count_tokens(message.role.value, model)
            
            # Name tokens if present
            if message.name:
                total_tokens += self.count_tokens(message.name, model)
            
            # Message formatting overhead
            total_tokens += self._get_message_overhead(model)
        
        # Conversation overhead
        total_tokens += self._get_conversation_overhead(model)
        
        return total_tokens
    
    def optimize_text_for_tokens(self, text: str, max_tokens: int, model: str = "gpt-3.5-turbo") -> str:
        """
        Truncate text to fit within token limit
        
        Args:
            text: Input text
            max_tokens: Maximum allowed tokens
            model: Model name
            
        Returns:
            Truncated text
        """
        current_tokens = self.count_tokens(text, model)
        
        if current_tokens <= max_tokens:
            return text
        
        # Binary search for optimal length
        left, right = 0, len(text)
        best_text = ""
        
        while left <= right:
            mid = (left + right) // 2
            candidate = text[:mid]
            
            if self.count_tokens(candidate, model) <= max_tokens:
                best_text = candidate
                left = mid + 1
            else:
                right = mid - 1
        
        return best_text
    
    def _count_with_tiktoken(self, text: str, model: str) -> int:
        """Count tokens using tiktoken (universal encoding)"""
        encoding_name = self._universal_encoding
        
        if encoding_name not in self._encoding_cache:
            self._encoding_cache[encoding_name] = tiktoken.get_encoding(encoding_name)
        
        encoding = self._encoding_cache[encoding_name]
        return len(encoding.encode(text))
    
    def _estimate_tokens(self, text: str) -> int:
        """Fallback token estimation"""
        language = self._detect_language(text)
        ratio = self._language_ratios.get(language, self._language_ratios["default"])
        
        char_count = len(re.sub(r'\s+', '', text))
        estimated_tokens = int(char_count * ratio)
        
        return max(1, estimated_tokens)
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection for estimation"""
        if re.search(r'[가-힣]', text):
            return "korean"
        elif re.search(r'[\u4e00-\u9fff]', text):
            return "chinese"
        elif re.search(r'[ひらがなカタカナ\u3040-\u309f\u30a0-\u30ff]', text):
            return "japanese"
        elif re.search(r'[а-яё]', text, re.IGNORECASE):
            return "russian"
        else:
            return "english"
    
    def _get_message_overhead(self, model: str) -> int:
        """Message formatting overhead (universal)"""
        return 3  # Universal overhead for all models
    
    def _get_conversation_overhead(self, model: str) -> int:
        """Conversation formatting overhead (universal)"""
        return 2  # Universal overhead for all models


# Convenience functions
def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Quick token counting"""
    counter = TokenCounter()
    return counter.count_tokens(text, model)


def count_message_tokens(messages: List[ChatMessage], model: str = "gpt-3.5-turbo") -> int:
    """Quick message token counting"""
    counter = TokenCounter()
    return counter.count_message_tokens(messages, model)


def optimize_for_tokens(text: str, max_tokens: int, model: str = "gpt-3.5-turbo") -> str:
    """Quick text optimization for token limits"""
    counter = TokenCounter()
    return counter.optimize_text_for_tokens(text, max_tokens, model)