"""
Data Extractor

Simple wrapper around json_extractor lib for extracting JSON from text.
KISS methodology - just extract JSON, nothing more.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from pydantic import BaseModel, ValidationError

from unrealon_llm.src.exceptions import ResponseParsingError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def _extract_json_smart(content: str) -> Optional[str]:
    """
    Smart JSON extraction from text - finds valid JSON objects/arrays.

    Args:
        content: Text content that may contain JSON

    Returns:
        First valid JSON string found or None
    """
    # Try to find JSON objects {} or arrays []
    patterns = [
        r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",  # Simple nested objects
        r"\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]",  # Simple nested arrays
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, content, re.DOTALL)
        for match in matches:
            json_candidate = match.group()
            try:
                # Test if it's valid JSON
                json.loads(json_candidate)
                return json_candidate
            except json.JSONDecodeError:
                continue

    # Fallback: find between outermost braces
    first_brace = content.find("{")
    if first_brace == -1:
        return None

    # Find matching closing brace
    brace_count = 0
    for i, char in enumerate(content[first_brace:], first_brace):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                return content[first_brace : i + 1]

    return None


def extract_json(
    content: str,
    expected_schema: Optional[Type[T]] = None,
    fallback_value: Optional[Any] = None,
    strict_mode: bool = True,
) -> Union[T, Dict[str, Any], None]:
    """
    Extract JSON from text content.

    Args:
        content: Text content containing JSON
        expected_schema: Pydantic model for validation
        fallback_value: Return value if extraction fails (non-strict mode)
        strict_mode: Raise exception on failure if True

    Returns:
        Extracted JSON data

    Raises:
        ResponseParsingError: If extraction fails in strict mode
    """
    if not content:
        if strict_mode:
            raise ResponseParsingError("Empty content", "json")
        return fallback_value

    try:
        # Smart JSON extraction
        json_content = _extract_json_smart(content)

        if json_content is None:
            if strict_mode:
                raise ResponseParsingError("No valid JSON found", "json")
            return fallback_value

        # Parse the extracted JSON
        extracted_data = json.loads(json_content)
        logger.info(f"Successfully extracted and parsed JSON: {type(extracted_data)}")

        # Validate with schema if provided
        if expected_schema and issubclass(expected_schema, BaseModel):
            return expected_schema.model_validate(extracted_data)

        return extracted_data

    except ValidationError as e:
        if strict_mode:
            raise e
        logger.warning(f"Schema validation failed: {e}")
        return fallback_value

    except Exception as e:
        if strict_mode:
            raise ResponseParsingError(content[:200], "json")
        logger.warning(f"JSON extraction failed: {e}")
        return fallback_value


def safe_extract_json(
    content: str,
    expected_schema: Optional[Type[T]] = None,
    fallback_value: Optional[Any] = None,
) -> Union[T, Dict[str, Any], None]:
    """
    Safe JSON extraction (non-strict mode).

    Args:
        content: Text content
        expected_schema: Optional schema
        fallback_value: Fallback value

    Returns:
        Extracted JSON or fallback
    """
    return extract_json(content, expected_schema, fallback_value, strict_mode=False)


def extract_llm_response_data(
    response_content: str,
    expected_schema: Optional[Type[T]] = None,
    required_fields: Optional[List[str]] = None,
) -> Union[T, Dict[str, Any]]:
    """
    Extract data from LLM response (strict mode).

    Args:
        response_content: LLM response text
        expected_schema: Pydantic model
        required_fields: Required fields to check

    Returns:
        Extracted and validated data

    Raises:
        ResponseParsingError: If extraction fails
    """
    result = extract_json(response_content, expected_schema, strict_mode=True)

    # Check required fields if no schema
    if not expected_schema and required_fields and isinstance(result, dict):
        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            raise ResponseParsingError(
                f"Missing required fields: {missing_fields}", "json"
            )

    return result


# Legacy compatibility
class SmartDataExtractor:
    """Simple wrapper for compatibility."""

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode

    def extract_json(self, content: str, expected_schema=None, fallback_value=None):
        return extract_json(content, expected_schema, fallback_value, self.strict_mode)


def create_data_extractor(strict_mode: bool = True) -> SmartDataExtractor:
    """Create data extractor instance."""
    return SmartDataExtractor(strict_mode)
