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

        return """{schema}

[__TASK_DESCRIPTION__]
Analyze this DETAILS/PRODUCT/ITEM page and generate universal extraction patterns.
PROCESSOR TYPE: {processor_type}
THIS IS A DETAILS PAGE containing information about a single item/product/service/article.
[/__TASK_DESCRIPTION__]

[__INSTRUCTIONS__]
YOUR TASK:
Analyze this details page and generate extraction patterns for ANY type of item.
This could be: product details, service info, article content, job description, real estate listing, person profile, etc.

CRITICAL REQUIREMENTS:
1. Return simple CSS selectors in the "selectors" object
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
