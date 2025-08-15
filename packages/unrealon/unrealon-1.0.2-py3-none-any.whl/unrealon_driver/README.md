# 🚀 UnrealOn Driver v3.0 - Revolutionary Web Automation

**Zero-configuration web automation framework with AI-first design and multiple execution modes.**

## ✨ Key Features

- 🎯 **Zero Configuration** - Everything works out of the box
- 🤖 **AI-First Design** - LLM integration as core feature  
- 🔌 **Multiple Execution Modes** - test, daemon, scheduled, interactive
- 🌐 **Smart Browser** - Intelligent automation with stealth
- ⏰ **Human-Readable Scheduling** - "30m", "1h", "daily"
- 📊 **Built-in Monitoring** - Enterprise observability

## 🚀 Quick Start

```python
from unrealon_driver import Parser

class MyParser(Parser):
    async def parse(self):
        return await self.browser.extract("https://example.com", ".item")

# Multiple execution modes
await MyParser().test()        # Development
await MyParser().daemon()      # Production WebSocket service  
await MyParser().schedule(every="30m")  # Automated execution
```

## 📦 Installation

```bash
# Full installation with all features
pip install unrealon-driver[full]

# Or minimal installation
pip install unrealon-driver
```

## 🎯 Execution Modes

### 🧪 Test Mode - Development & Debugging
```python
result = await parser.test()
print(result)
```

### 🔌 Daemon Mode - Production WebSocket Service
```python
await parser.daemon(
    server="wss://your-server.com",
    api_key="your_key"
)
```

### ⏰ Scheduled Mode - Automated Execution
```python
# Every 30 minutes
await parser.schedule(every="30m")

# Daily at 9 AM
await parser.schedule(every="daily", at="09:00")
```

### 🎮 Interactive Mode - Live Development
```python
await parser.interactive()
```

## 🤖 AI-Powered Extraction

```python
class AIParser(Parser):
    async def parse(self):
        html = await self.browser.get_html("https://shop.com")
        
        # AI-powered structured extraction
        products = await self.llm.extract(html, schema={
            "products": [{
                "name": "string",
                "price": "number",
                "rating": "number"
            }]
        })
        
        return products
```

## 🌐 Smart Browser Features

```python
class BrowserParser(Parser):
    async def parse(self):
        # Simple extraction
        headlines = await self.browser.extract(
            "https://news.com", 
            ".headline",
            limit=10
        )
        
        # Structured extraction
        products = await self.browser.extract_structured(
            "https://shop.com",
            schema={
                "name": ".product-name",
                "price": ".price", 
                "rating": ".rating"
            }
        )
        
        return {"headlines": headlines, "products": products}
```

## 📊 Built-in Monitoring

All execution modes include comprehensive monitoring:

- ✅ Performance metrics
- ✅ Error tracking and recovery
- ✅ Health monitoring  
- ✅ Cost management (AI features)
- ✅ Automatic logging

## 🏗️ Architecture

UnrealOn Driver v3.0 is built on top of battle-tested components:

- **🌐 Browser**: [unrealon-browser] - Advanced browser automation
- **🤖 LLM**: [unrealon-llm] - AI-powered extraction  
- **🔌 SDK**: [unrealon-sdk] - Enterprise connectivity
- **📝 Logging**: Integrated structured logging
- **📊 Metrics**: Built-in observability

## 🔧 Configuration

### Zero Configuration (Default)
```python
# Works immediately without setup
parser = MyParser()
await parser.test()
```

### Environment Variables
```bash
# Optional configuration
export UNREALON_API_KEY="your_key"
export UNREALON_LLM_PROVIDER="openrouter"
export UNREALON_BROWSER_HEADLESS="false"  # For debugging
```

### Custom Configuration
```python
parser = MyParser(
    config={
        "browser": {"headless": False},
        "llm": {"daily_cost_limit": 10.0},
        "logger": {"log_level": "DEBUG"}
    }
)
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_parser.py

# Run with coverage
pytest --cov=src tests/
```

## 📚 Documentation

Complete documentation is available in the `@docs/` directory:

- **[Getting Started](@docs/modules/quick-start.md)** - 5-minute quick start
- **[Parser Guide](@docs/modules/parser.md)** - Complete parser documentation
- **[Browser Automation](@docs/modules/browser.md)** - Smart browser features
- **[AI Extraction](@docs/modules/llm.md)** - LLM integration guide
- **[Daemon Mode](@docs/modules/daemon.md)** - Production deployment
- **[Scheduling](@docs/modules/scheduling.md)** - Automated execution
- **[Architecture](@docs/architecture/overview.md)** - Technical overview

## 🤝 Contributing

UnrealOn Driver v3.0 is part of the UnrealOn ecosystem. See the main repository for contribution guidelines.

## 📄 License

MIT License - see LICENSE file for details.

## 🚀 What's New in v3.0

- **Revolutionary Simplicity**: Zero configuration required
- **AI-First Design**: LLM integration as core feature, not add-on
- **Modern Architecture**: Built from scratch for cloud-native deployment
- **Multiple Execution Modes**: Unified API for all use cases
- **Enterprise Ready**: Production monitoring and scaling built-in

---

**Built with ❤️ by the UnrealOn Team**
