# UnrealOn LLM SDK

AI-powered modular platform for content processing with cost control and accuracy guarantees.

## Features

- **Universal LLM Client**: Support for OpenRouter, OpenAI, Anthropic
- **HTML Pattern Detection**: AI-powered analysis and selector generation
- **Smart Translation**: Language detection with caching
- **JSON Processing**: Intelligent data transformation
- **Type Generation**: Pydantic and TypeScript schema creation
- **Cost Control**: Real-time budget tracking and limits
- **Type Safety**: 100% Pydantic v2 compliance

## Quick Start

```python
from unrealon_llm import UnrealOnLLM, LLMConfig

# Initialize with API keys
config = LLMConfig(
    openrouter_api_key="sk-or-v1-...",
    daily_cost_limit_usd=10.0
)

llm = UnrealOnLLM(config)

# Analyze HTML and generate selectors
result = await llm.process_html_to_types(
    html_content="<div class='product'>...</div>",
    target_elements=["title", "price"],
    target_language="en"
)
```

## Installation

```bash
pip install unrealon-llm
```

## Documentation

See the full documentation in the `@docs` directory.
