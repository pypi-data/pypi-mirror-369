# UnrealOn SDK

Core SDK for UnrealOn parser development with WebSocket communication and enterprise services.

## Features

- WebSocket client for real-time communication
- Auto-generated API models
- Enterprise services (proxy, monitoring, etc.)
- CLI tools for SDK management

## Installation

```bash
pip install unrealon-sdk
```

## Usage

```python
from unrealon_sdk import AdapterClient, AdapterConfig

config = AdapterConfig()
client = AdapterClient(config)
```
