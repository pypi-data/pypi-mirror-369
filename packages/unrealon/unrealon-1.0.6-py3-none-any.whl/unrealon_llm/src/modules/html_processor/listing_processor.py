"""
Listing Processor

Universal processor for listing/catalog pages.
Handles ANY type of listings: products, services, articles, real estate, jobs, etc.
"""

from typing import Type

from .base_processor import BaseHTMLProcessor
from .models import UniversalExtractionSchema


class ListingProcessor(BaseHTMLProcessor):
    """Universal listing page pattern extractor"""

    def get_processor_type(self) -> str:
        """Return processor type identifier"""
        return "listing"

    def get_schema_class(self) -> Type[UniversalExtractionSchema]:
        """Return Pydantic schema class for listing extraction"""
        return UniversalExtractionSchema

    def get_extraction_prompt_template(self) -> str:
        """Return listing-specific extraction prompt template"""

        prompt = """{schema}

        [__TASK_DESCRIPTION__]
        Analyze this LISTING/CATALOG page and generate universal extraction patterns.
        PROCESSOR TYPE: {processor_type}
        THIS IS A LISTING PAGE containing multiple items arranged in a list or grid.
        [/__TASK_DESCRIPTION__]

        [__CRITICAL_FORMAT_REQUIREMENTS__]
        🚨 SELECTORS FORMAT: The "selectors" field MUST be a DICTIONARY/OBJECT, NOT a list!
        Example of CORRECT format:
        "selectors": {{
            "items_container": ["div.product-grid", "ul.product-list", "div.items"],
            "item_title": ["h3.product-title", "a.product-link", ".item-name"],
            "item_price": [".price", ".cost", "span[data-price]"],
            "item_image": ["img.product-image", ".item-img", "img[src*='product']"],
            "pagination": [".pagination", ".page-nav", "nav[aria-label='pagination']"]
        }}

        ❌ WRONG format (DO NOT USE):
        "selectors": ["div.product", "h3.title", ".price"]

        ✅ CORRECT format (USE THIS):
        "selectors": {{
            "items": ["div.product", "li.item", ".product-card"],
            "titles": ["h3.title", ".product-name", "a[title]"],
            "prices": [".price", ".cost", "span[data-price]"]
        }}
        [/__CRITICAL_FORMAT_REQUIREMENTS__]

        [__INSTRUCTIONS__]
        YOUR TASK:
        Analyze this listing page and generate extraction patterns for ANY type of items.
        This could be: products, services, articles, jobs, real estate, people, cars, etc.

        CRITICAL REQUIREMENTS:
        1. The "selectors" field MUST be a DICTIONARY with field names as keys and arrays of CSS selectors as values
        2. This is a LISTING PAGE with multiple items
        3. Focus on identifying item containers and individual item patterns
        4. Detect ANY type of items - not just products!
        5. Provide multiple fallback selectors for reliability
        6. Include pagination and navigation patterns
        7. Use realistic confidence scores (0.1-1.0)
        8. Auto-detect what type of content this listing contains
        9. Provide extraction strategy advice
        10. Look for structured data (JSON-LD, microdata)
        11. Generate patterns that work with BeautifulSoup4 .select() method
        12. RETURN JSON that EXACTLY matches the Pydantic schema above!

        ANALYZE THE HTML AND DETERMINE:
        - What type of items are listed (products, services, articles, etc.)
        - How items are structured and contained
        - What navigation elements exist
        - What metadata is available
        - Best extraction strategy for this specific page
        [/__INSTRUCTIONS__]

        [__HTML_CONTENT__]
        HTML CONTENT (first 50KB):
        {html_content}
        [/__HTML_CONTENT__]
        """

        return self._trim_system_prompt(prompt)
