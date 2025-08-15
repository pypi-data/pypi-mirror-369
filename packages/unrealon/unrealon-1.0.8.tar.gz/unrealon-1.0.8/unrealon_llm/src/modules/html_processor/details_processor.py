"""
Details Processor

Universal processor for detail/product/item pages.
Handles ANY type of detail pages: product details, service info, article content, job descriptions, etc.
"""

from typing import Type

from .base_processor import BaseHTMLProcessor
from .models import UniversalExtractionSchema


class DetailsProcessor(BaseHTMLProcessor):
    """Universal details page pattern extractor"""

    def get_processor_type(self) -> str:
        """Return processor type identifier"""
        return "details"

    def get_schema_class(self) -> Type[UniversalExtractionSchema]:
        """Return Pydantic schema class for details extraction"""
        return UniversalExtractionSchema

    def get_extraction_prompt_template(self) -> str:
        """Return details-specific extraction prompt template"""

        prompt = """{schema}
        [__TASK_DESCRIPTION__]
        Analyze this DETAILS/PRODUCT/ITEM page and generate universal extraction patterns.
        PROCESSOR TYPE: {processor_type}
        THIS IS A DETAILS PAGE containing information about a single item/product/service/article.
        [/__TASK_DESCRIPTION__]

        [__CRITICAL_FORMAT_REQUIREMENTS__]
        🚨 SELECTORS FORMAT: The "selectors" field MUST be a DICTIONARY/OBJECT, NOT a list!
        Example of CORRECT format:
        "selectors": {{
            "title": ["h1.product-title", "h1.page-title", ".item-name"],
            "price": [".price", ".cost", "span[data-price]", ".product-price"],
            "description": [".description", ".product-desc", ".item-details"],
            "images": ["img.product-image", ".gallery img", "img[src*='product']"],
            "specifications": [".specs", ".product-specs", ".item-specifications"],
            "reviews": [".reviews", ".product-reviews", ".customer-reviews"]
        }}

        ❌ WRONG format (DO NOT USE):
        "selectors": ["h1.title", ".price", ".description"]

        ✅ CORRECT format (USE THIS):
        "selectors": {{
            "title": ["h1.title", ".product-name", "h1[itemprop='name']"],
            "price": [".price", ".cost", "span[data-price]"],
            "description": [".description", ".product-desc", ".item-details"]
        }}
        [/__CRITICAL_FORMAT_REQUIREMENTS__]

        [__INSTRUCTIONS__]
        YOUR TASK:
        Analyze this details page and generate extraction patterns for ANY type of item.
        This could be: product details, service info, article content, job description, real estate listing, person profile, etc.

        CRITICAL REQUIREMENTS:
        1. The "selectors" field MUST be a DICTIONARY with field names as keys and arrays of CSS selectors as values
        2. Include comprehensive markdown documentation
        3. Provide real examples from the actual HTML
        4. Explain the page structure and best extraction approach
        5. Include confidence scores and fallback strategies
        6. Document any special handling needed

        ANALYZE THE HTML AND DETERMINE:
        - What type of item this page describes
        - What information is available (specs, pricing, reviews, etc.)
        - How content is structured and organized
        - What actions are possible (buy, contact, etc.)
        - Best extraction strategy for this specific page
        [/__INSTRUCTIONS__]

        [__HTML_CONTENT__]
        HTML CONTENT (first 50KB):
        {html_content}
        [/__HTML_CONTENT__]
        """

        return self._trim_system_prompt(prompt)
