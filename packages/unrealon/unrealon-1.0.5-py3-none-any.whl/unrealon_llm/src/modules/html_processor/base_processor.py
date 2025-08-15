"""
Base HTML Processor

Universal base class for HTML pattern extraction processors.
Provides common functionality for listing and details processors.
"""

from abc import ABC, abstractmethod
import json
import random
from typing import Type
import traceback

from unrealon_llm.src.core import SmartLLMClient
from unrealon_llm.src.dto import ChatMessage, MessageRole
from unrealon_llm.src.utils.html_cleaner import SmartHTMLCleaner
from unrealon_llm.src.utils.data_extractor import SmartDataExtractor
from unrealon_llm.src.llm_logging import (
    get_llm_logger,
    initialize_development_logger,
    initialize_llm_logger,
)

from .models import (
    UniversalExtractionSchema,
    ProcessingInfo,
    ExtractionResult,
)

# Ensure loggers are initialized
logger = get_llm_logger()
if logger is None:
    try:
        initialize_development_logger()
        initialize_llm_logger()
        logger = get_llm_logger()
    except:
        logger = None


class BaseHTMLProcessor(ABC):
    """Base class for HTML pattern extraction processors"""

    def __init__(self, llm_client: SmartLLMClient):
        """
        Initialize base processor

        Args:
            llm_client: LLM client for AI analysis
        """
        self.llm_client = llm_client
        self.cleaner = SmartHTMLCleaner()
        self.data_extractor = SmartDataExtractor()

        # Get processor-specific configuration
        self.processor_type = self.get_processor_type()
        self.schema_class = self.get_schema_class()

        logger.log_html_analysis_start(
            html_size_bytes=0,  # Will be filled when processing
            target_elements=[self.processor_type],
            details={"processor_class": self.__class__.__name__},
        )

    @abstractmethod
    def get_processor_type(self) -> str:
        """Return processor type identifier"""
        pass

    @abstractmethod
    def get_schema_class(self) -> Type:
        """Return Pydantic schema class for this processor"""
        pass

    @abstractmethod
    def get_extraction_prompt_template(self) -> str:
        """Return extraction prompt template for this processor type"""
        pass

    async def extract_patterns(self, html_content: str) -> ExtractionResult:
        """
        Extract patterns from HTML using LLM intelligence

        Args:
            html_content: Raw HTML content

        Returns:
            ExtractionResult: Validated Pydantic result with extraction patterns and processing metadata
        """
        logger.log_html_analysis_start(
            html_size_bytes=len(html_content),
            target_elements=[self.processor_type],
            details={"processor_type": self.processor_type},
        )

        # Clean HTML first with aggressive cleaning for LLM analysis
        cleaned_html, extracted_data = self.cleaner.clean_html(
            html_content, preserve_js_data=True, aggressive_cleaning=True
        )

        cleaning_stats = self.cleaner.get_cleaning_stats(html_content, cleaned_html)
        logger.log_html_cleaning(
            original_size_bytes=len(html_content),
            cleaned_size_bytes=len(cleaned_html),
            optimization_type="aggressive",
            details=cleaning_stats,
        )

        # Build extraction prompt
        prompt = self._build_extraction_prompt(cleaned_html)

        # Log the full prompt for debugging
        logger.log_llm_request_start(
            provider="debug",
            model="prompt_debug",
            prompt_tokens=0,
            details={
                "full_prompt": prompt[:2000] + "..." if len(prompt) > 2000 else prompt,
                "schema_json": json.dumps(self.schema_class.model_json_schema(), indent=2)
            }
        )

        # Prepare LLM messages
        messages = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=f"You are an HTML-to-JSON expert at analyzing {self.processor_type} pages. You MUST return JSON that EXACTLY matches the Pydantic schema provided. RESPOND ONLY WITH VALID JSON. NO EXPLANATIONS, NO TEXT, ONLY JSON! Include ALL required fields from the schema!",
            ),
            ChatMessage(
                role=MessageRole.USER,
                content=prompt
                + "\n\nRESPOND ONLY WITH JSON! START WITH { AND END WITH }. NO OTHER TEXT!",
            ),
        ]

        logger.log_llm_request_start(
            provider="openrouter",
            model=getattr(self.llm_client, "model", "unknown"),
            prompt_tokens=len(prompt) // 4,  # rough estimate
            details={"processor_type": self.processor_type},
        )

        response = None
        try:
            # Call LLM
            response = await self.llm_client.chat_completion(
                messages, 
                response_model=self.schema_class
            )

            # Log full LLM response for debugging
            logger.log_llm_response_received(
                provider="openrouter",
                model=getattr(response, "model", "unknown"),
                completion_tokens=(
                    getattr(response.usage, "completion_tokens", 0)
                    if hasattr(response, "usage")
                    else 0
                ),
                total_tokens=(
                    getattr(response.usage, "total_tokens", 0)
                    if hasattr(response, "usage")
                    else 0
                ),
                cost_usd=getattr(response, "cost_usd", 0.0),
                details={"raw_response_full": response.content},
            )

            # Use the validated model from LLM response
            if hasattr(response, 'extracted_model') and response.extracted_model:
                validated_model = response.extracted_model
                validated_result = validated_model.model_dump()
                logger.log_html_analysis_completed(
                    selectors_generated=len(str(validated_result)),
                    confidence_score=validated_result.get("confidence", 0.0),
                    details={
                        "processor_type": self.processor_type,
                        "validation_success": True,
                        "schema_matched": True,
                    },
                )
            else:
                # Fallback: parse manually if no model provided
                result_data = self.data_extractor.extract_json(response.content)
                try:
                    validated_model = self.schema_class(**result_data)
                    validated_result = validated_model.model_dump()
                    logger.log_html_analysis_completed(
                        selectors_generated=len(str(result_data)),
                        confidence_score=result_data.get("confidence", 0.0),
                        details={
                            "processor_type": self.processor_type,
                            "validation_success": True,
                            "schema_matched": True,
                        },
                    )
                except Exception as e:
                    logger.log_html_analysis_failed(
                        error_message=f"Pydantic validation failed: {str(e)}",
                        details={
                            "processor_type": self.processor_type,
                            "validation_error": str(e),
                            "raw_llm_response": result_data,
                        },
                    )
                    # Fall back to raw data
                    validated_result = result_data

            # Create Pydantic processing metadata
            processing_info = ProcessingInfo(
                original_html_size=len(html_content),
                cleaned_html_size=len(cleaned_html),
                cleaning_stats=cleaning_stats,
                extracted_js_data=extracted_data,
                processor_type=self.processor_type,
                llm_model=getattr(response, "model", "unknown"),
                tokens_used=(
                    getattr(response.usage, "total_tokens", 0)
                    if hasattr(response, "usage")
                    else 0
                ),
                cost_usd=getattr(response, "cost_usd", 0.0),
            )

            # Return validated Pydantic result
            return ExtractionResult(
                extraction_result=validated_result,
                processing_info=processing_info,
            )

        except Exception as e:
            logger.log_html_analysis_failed(
                error_message=str(e),
                details={
                    "processor_type": self.processor_type,
                    "raw_response": getattr(response, "content", "No response"),
                    "traceback": traceback.format_exc(),
                },
            )
            raise

    def _build_extraction_prompt(self, cleaned_html: str) -> str:
        """Build extraction prompt using processor-specific template"""
        # Processors handle their own prompt construction with schema and HTML
        # Just get the template and let it handle the details
        prompt_template = self.get_extraction_prompt_template()

        # Use more content for better analysis, but still respect token limits
        html_limit = 50000  # Increase from 15K to 50K characters

        # Build full prompt with auto-generated Pydantic 2 schema
        schema_json = json.dumps(self.schema_class.model_json_schema(), indent=2)

        # Add random number to bypass any caching
        cache_buster = random.randint(100000, 999999)
        
        schema_prompt = f"""PYDANTIC 2 SCHEMA (Request #{cache_buster}):
{schema_json}

CRITICAL: Return JSON that EXACTLY matches this schema structure!
The response must include ALL required fields: detected_item_type, extraction_strategy, confidence, selectors, documentation."""

        return prompt_template.format(
            processor_type=self.processor_type,
            html_content=cleaned_html[:html_limit]
            + ("..." if len(cleaned_html) > html_limit else ""),
            schema=schema_prompt,
        )

    def get_cost_estimate(self, html_content: str) -> float:
        """
        Estimate cost for processing HTML content

        Args:
            html_content: HTML content to estimate

        Returns:
            Estimated cost in USD
        """
        # Clean HTML to get realistic token count
        cleaned_html, _ = self.cleaner.clean_html(
            html_content, aggressive_cleaning=True
        )

        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = len(cleaned_html) / 4

        # Add prompt overhead (approximately 500 tokens)
        total_tokens = estimated_tokens + 500

        # Estimate cost (Claude Haiku: ~$0.25 per 1M input tokens)
        estimated_cost = (total_tokens / 1_000_000) * 0.25

        return estimated_cost
