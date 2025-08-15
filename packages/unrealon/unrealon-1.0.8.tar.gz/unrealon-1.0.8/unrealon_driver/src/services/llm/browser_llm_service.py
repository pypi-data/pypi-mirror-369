"""
Browser LLM Service - UnrealOn Driver v3.0

Simple URL → Browser → HTML → LLM → Response workflow.
Just like the old driver but with v3.0 improvements.
"""

import asyncio
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from urllib.parse import urlparse

from unrealon_driver.src.services.browser_service import BrowserService
from unrealon_driver.src.services.llm.llm import LLMService
from unrealon_driver.src.dto.services import DriverBrowserConfig, LLMConfig
from unrealon_driver.src.config.auto_config import AutoConfig
from unrealon_driver.src.logging.driver_logger import DriverLogger
from unrealon_driver.src.services.metrics_service import MetricsService


class BrowserLLMConfig(BaseModel):
    """Configuration for Browser LLM Service."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Browser settings
    browser_config: DriverBrowserConfig = Field(
        ..., description="Browser configuration"
    )

    # LLM settings
    llm_config: LLMConfig = Field(..., description="LLM configuration")

    # Processing settings - removed dom_wait_seconds as unnecessary

    # Output settings
    save_results: bool = Field(
        default=True, description="Save extraction results to files"
    )
    results_dir: Optional[str] = Field(
        default=None, description="Directory for saving results"
    )


class ExtractionResult(BaseModel):
    """Result of browser + LLM extraction operation."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Core data
    data: dict = Field(..., description="Extracted structured data")
    url: str = Field(..., description="Source URL")
    extraction_id: str = Field(..., description="Unique extraction identifier")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Extraction timestamp"
    )

    # Performance metrics
    total_duration_seconds: float = Field(
        ..., ge=0, description="Total operation duration"
    )
    browser_duration_seconds: float = Field(
        ..., ge=0, description="Browser operation duration"
    )
    llm_duration_seconds: float = Field(
        ..., ge=0, description="LLM processing duration"
    )

    # Content metrics
    html_size_bytes: int = Field(..., ge=0, description="HTML content size")
    success: bool = Field(..., description="Whether extraction was successful")

    # NEW: Additional data for comprehensive saving like html_processor_demo
    original_html: str = Field(default="", description="Original HTML content")
    cleaned_html: str = Field(default="", description="Cleaned HTML content")

    # File paths (if saved)
    result_file_path: Optional[str] = Field(
        default=None, description="Path to saved result file"
    )
    original_html_path: Optional[str] = Field(
        default=None, description="Path to saved original HTML"
    )
    cleaned_html_path: Optional[str] = Field(
        default=None, description="Path to saved cleaned HTML"
    )
    markdown_docs_path: Optional[str] = Field(
        default=None, description="Path to saved markdown documentation"
    )


class BrowserLLMService:
    """
    🌐 Browser + LLM Service - Simple Integration

    Simple URL → Browser → HTML → LLM → Data workflow:

    Main methods:
    - extract_listing(url) - for search results, catalogs
    - extract_details(url) - for product pages, articles

    Example:
        service = BrowserLLMService(config)
        result = await service.extract_listing("https://amazon.com/s?k=laptop")
        result = await service.extract_details("https://amazon.com/dp/B123456")
    """

    def __init__(
        self,
        config=None,
        auto_config: AutoConfig = None,
        logger: DriverLogger = None,
        metrics: MetricsService = None,
    ):
        """
        Initialize Browser + LLM service.

        Args:
            config: BrowserLLMConfig (legacy method)
            auto_config: AutoConfig with ready browser/llm configs (NEW SIMPLE METHOD!)
            logger: Logger instance
            metrics: Metrics service
        """
        self.logger = logger
        self.metrics = metrics

        # 🔥 NEW SIMPLE METHOD: Use AutoConfig directly!
        if auto_config:
            self.config = BrowserLLMConfig(
                browser_config=auto_config.browser_config,
                llm_config=auto_config.llm_config,
                save_results=True,
                results_dir=str(auto_config.system_dir / "results"),
            )
        elif config:
            # Legacy method for backward compatibility
            self.config = config
        else:
            raise ValueError("Either config or auto_config must be provided")

        # Initialize component services
        self.browser_service = BrowserService(
            config=self.config.browser_config,
            logger=logger,
            metrics=metrics,
        )

        self.llm_service = LLMService(config=self.config.llm_config, logger=logger)

        # Setup results directory
        if self.config.save_results and self.config.results_dir:
            self.results_dir = Path(self.config.results_dir)
            self.results_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.results_dir = None

        if self.logger:
            self.logger.info("🌐 BrowserLLMService initialized successfully")

    async def extract_listing(self, url: str) -> ExtractionResult:
        """Extract listing data from URL (e.g., search results, category pages)."""
        return await self._extract_from_url(url, "listing")

    async def extract_details(self, url: str) -> ExtractionResult:
        """Extract detail data from URL (e.g., product page, item details)."""
        return await self._extract_from_url(url, "details")

    async def _extract_from_url(self, url: str, page_type: str) -> ExtractionResult:
        """
        Private method: Extract structured data from URL using Browser → LLM workflow.

        Args:
            url: Target URL to extract from
            page_type: "listing" or "details" for proper LLM routing

        Returns:
            ExtractionResult with data and metadata
        """
        extraction_id = f"extract_{int(datetime.utcnow().timestamp())}"
        start_time = datetime.utcnow()

        if self.logger:
            self.logger.info(f"🌐 Extracting {page_type} from: {url}")

        try:
            # Step 1: Browser → HTML
            browser_start = datetime.utcnow()
            html_content = await self.browser_service.get_html(url)
            browser_duration = (datetime.utcnow() - browser_start).total_seconds()

            # Step 2: LLM processing
            llm_start = datetime.utcnow()
            if page_type == "listing":
                extracted_data = await self.llm_service.process_listing(html_content)
            else:
                extracted_data = await self.llm_service.process_details(html_content)
            llm_duration = (datetime.utcnow() - llm_start).total_seconds()

            # Step 3: Get cleaned HTML from LLM service's processor
            cleaned_html = ""
            try:
                if page_type == "listing" and self.llm_service.listing_processor:
                    processor = self.llm_service.listing_processor
                elif self.llm_service.details_processor:
                    processor = self.llm_service.details_processor
                else:
                    processor = None

                if processor and hasattr(processor, "cleaner"):
                    cleaned_html, _ = processor.cleaner.clean_html(
                        html_content, preserve_js_data=True, aggressive_cleaning=True
                    )
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Could not get cleaned HTML: {e}")

                cleaned_html = html_content  # Fallback to original

            # Step 4: Create result
            total_duration = (datetime.utcnow() - start_time).total_seconds()

            result = ExtractionResult(
                data=extracted_data,
                url=url,
                extraction_id=extraction_id,
                total_duration_seconds=total_duration,
                browser_duration_seconds=browser_duration,
                llm_duration_seconds=llm_duration,
                html_size_bytes=len(html_content.encode()),
                success=True,
                # NEW: Additional data
                original_html=html_content,
                cleaned_html=cleaned_html,
            )

            # Step 4: Save results if configured
            if self.config.save_results and self.results_dir:
                await self._save_extraction_result(result)

            if self.logger:
                self.logger.info(
                    f"✅ {page_type.title()} extraction completed in {total_duration:.2f}s"
                )

            return result

        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ {page_type.title()} extraction failed: {e}")

            # Create failed result
            total_duration = (datetime.utcnow() - start_time).total_seconds()
            return ExtractionResult(
                data={},
                url=url,
                extraction_id=extraction_id,
                total_duration_seconds=total_duration,
                browser_duration_seconds=0,
                llm_duration_seconds=0,
                html_size_bytes=0,
                success=False,
                original_html="",
                cleaned_html="",
            )

    async def _save_extraction_result(self, result: ExtractionResult) -> None:
        """Save comprehensive extraction results to files (JSON, HTML, MD) like html_processor_demo."""
        if not self.results_dir:
            return

        # Create listing-specific folder and clear old results
        listing_folder = self._create_listing_folder(result.url)

        # Determine page type for filenames
        page_type = "listing" if "listing" in result.extraction_id else "details"
        base_filename = f"{result.extraction_id}_{page_type}"

        # 1. Save main result as JSON
        result_file = listing_folder / f"{base_filename}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            # Create clean data without huge HTML content for JSON
            clean_data = result.model_dump()
            # Don't save HTML content in JSON (too large)
            clean_data["original_html"] = f"<saved to {base_filename}_original.html>"
            clean_data["cleaned_html"] = f"<saved to {base_filename}_cleaned.html>"
            json.dump(clean_data, f, ensure_ascii=False, indent=2, default=str)
        result.result_file_path = str(result_file)

        # 2. Save original HTML
        if result.original_html:
            original_html_file = listing_folder / f"{base_filename}_original.html"
            with open(original_html_file, "w", encoding="utf-8") as f:
                f.write(result.original_html)
            result.original_html_path = str(original_html_file)

        # 3. Save cleaned HTML
        if result.cleaned_html:
            cleaned_html_file = listing_folder / f"{base_filename}_cleaned.html"
            with open(cleaned_html_file, "w", encoding="utf-8") as f:
                f.write(result.cleaned_html)
            result.cleaned_html_path = str(cleaned_html_file)

        # 4. Generate and save markdown documentation (like html_processor_demo)
        result_dict = result.data if isinstance(result.data, dict) else {}
        self._save_markdown_documentation(result_dict, f"{base_filename}_documentation")

        if self.logger:
            self.logger.info(f"💾 Comprehensive results saved to: {listing_folder}")
            self.logger.info(f"📊 JSON: {result_file.name}")
            self.logger.info(
                f"🌐 HTML: {base_filename}_original.html, {base_filename}_cleaned.html"
            )
            self.logger.info(f"📝 Docs: {markdown_file.name}")

    def _create_listing_folder(self, url: str) -> Path:
        """Create folder for listing based on URL and clear if exists."""
        # Simple folder name from URL host
        host = urlparse(url).netloc.replace("www.", "")
        folder_name = re.sub(r"[^\w\-_]", "_", host) or "listing"

        # Create folder path
        listing_folder = self.results_dir / folder_name

        # Clear folder if exists (new LLM cycle)
        if listing_folder.exists():
            if self.logger:
                self.logger.info(f"🗑️ Clearing existing folder: {listing_folder}")
            shutil.rmtree(listing_folder)

        # Create fresh folder
        listing_folder.mkdir(parents=True, exist_ok=True)

        if self.logger:
            self.logger.info(f"📁 Created listing folder: {listing_folder}")

        return listing_folder

    def _save_markdown_documentation(self, result_dict: dict, filename: str):
        """Save markdown documentation from selectors"""
        extraction_result = result_dict.get("extraction_result", {})
        selectors = extraction_result.get("selectors", {})
        documentation = extraction_result.get("documentation", "")

        filepath = self.results_dir / f"{filename}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(documentation)
        print(f"Markdown documentation saved to: {filepath}")

    async def cleanup(self):
        """Clean up service resources."""
        await self.browser_service.cleanup()
        await self.llm_service.cleanup()

        if self.logger:
            self.logger.info("🌐 BrowserLLMService cleanup completed")

    def __repr__(self) -> str:
        return f"<BrowserLLMService(parser_id={self.config.browser_config.parser_id})>"
