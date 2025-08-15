"""
🤖 LLM Service - UnrealOn Driver v3.0

Simple wrapper around UnrealOn LLM for HTML processing.
Just pass HTML and get parsed results.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from unrealon_llm.src.provider import UnrealOnLLM
from unrealon_sdk.src.enterprise.logging.development import get_development_logger
from unrealon_sdk.src.dto.logging import SDKContext, SDKEventType

from unrealon_driver.src.dto.services import LLMConfig
from unrealon_driver.src.core.exceptions import create_llm_error


class LLMService:
    """
    Simple LLM service for HTML processing.
    
    Two main methods:
    - process_listing(html) - for catalog/listing pages  
    - process_details(html) - for product/detail pages
    
    Example:
        llm = LLMService(config)
        result = await llm.process_listing(html_content)
        result = await llm.process_details(html_content)
    """
    
    def __init__(self, config: LLMConfig, logger=None):
        """
        Initialize LLM service.
        
        Args:
            config: LLMConfig with API key and settings
            logger: Optional logger
        """
        self.config = config
        self.logger = logger
        
        # ✅ DEVELOPMENT LOGGER INTEGRATION
        self.dev_logger = get_development_logger()
        
        # Initialize processors immediately (no lazy loading bullshit)
        if config.api_key:
            self.listing_processor = UnrealOnLLM.create_listing_processor(
                openrouter_api_key=config.api_key,
                default_model=config.model,
                daily_cost_limit=1.0,  # Default $1 per day
                enable_caching=config.enable_caching
            )
            
            self.details_processor = UnrealOnLLM.create_details_processor(
                openrouter_api_key=config.api_key,
                default_model=config.model,
                daily_cost_limit=1.0,  # Default $1 per day
                enable_caching=config.enable_caching
            )
        else:
            # For tests - create mock processors
            self.listing_processor = None
            self.details_processor = None
        
        if self.logger:
            self.logger.info(f"🤖 LLM service initialized with {config.provider}")
        
        # Log initialization with development logger
        if self.dev_logger:
            self.dev_logger.log_info(
                SDKEventType.COMPONENT_CREATED,
                "LLM service initialized",
                context=SDKContext(
                    component_name="LLM",
                    layer_name="UnrealOn_Driver",
                    metadata={
                        "provider": config.provider,
                        "model": config.model,
                        "cost_tracking": config.enable_cost_tracking
                    }
                )
            )
    
    async def process_listing(self, html: str) -> dict:
        """
        Process listing/catalog page HTML.
        
        Args:
            html: Raw HTML content
            
        Returns:
            Extracted data as dict
        """
        try:
            if self.logger:
                self.logger.info("🔍 Processing listing page")
            
            if not self.listing_processor:
                return {"test_data": "mock_listing_result"}
                
            result = await self.listing_processor.extract_patterns(html)
            
            if self.logger:
                self.logger.info("✅ Listing processing complete")
            
            return self._convert_result(result)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Listing processing failed: {e}")
            
            # 🔥 FALLBACK: If LLM validation fails, return basic structure
            if "Input should be a valid dictionary" in str(e) or "must be a mapping" in str(e):
                return {
                    "extracted_data": "LLM validation failed - Claude returned list instead of dict",
                    "error": "LLM_VALIDATION_ERROR",
                    "raw_error": str(e),
                    "extraction_result": {
                        "selectors": {},
                        "documentation": "Extraction failed due to LLM format validation",
                        "detected_item_type": "validation_error"
                    }
                }
            
            raise create_llm_error(
                f"Listing processing failed: {e}",
                provider=self.config.provider,
                model=self.config.model,
                input_size=len(html)
            )
    
    async def process_details(self, html: str) -> dict:
        """
        Process detail/product page HTML.
        
        Args:
            html: Raw HTML content
            
        Returns:
            Extracted data as dict
        """
        try:
            if self.logger:
                self.logger.info("🔍 Processing details page")
            
            if not self.details_processor:
                return {"test_data": "mock_details_result"}
                
            result = await self.details_processor.extract_patterns(html)
            
            if self.logger:
                self.logger.info("✅ Details processing complete")
            
            return self._convert_result(result)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Details processing failed: {e}")
            raise create_llm_error(
                f"Details processing failed: {e}",
                provider=self.config.provider,
                model=self.config.model,
                input_size=len(html)
            )
    
    def _convert_result(self, result) -> dict:
        """Convert LLM result to simple dict."""
        try:
            # 🔥 FIX: Use model_dump() like in working example!
            if result:
                return result.model_dump()
            return {"extracted_data": "No extraction result found"}
        except Exception as e:
            return {"extracted_data": f"Error converting result: {e}"}
    
    async def cleanup(self):
        """Clean up LLM resources."""
        try:
            if hasattr(self.listing_processor, 'llm_client') and self.listing_processor.llm_client:
                await self.listing_processor.llm_client.close()
                
            if hasattr(self.details_processor, 'llm_client') and self.details_processor.llm_client:
                await self.details_processor.llm_client.close()
                
            if self.logger:
                self.logger.info("🤖 LLM service cleanup completed")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ LLM cleanup error: {e}")
    
    def __repr__(self) -> str:
        return f"<LLMService(provider={self.config.provider}, model={self.config.model})>"
