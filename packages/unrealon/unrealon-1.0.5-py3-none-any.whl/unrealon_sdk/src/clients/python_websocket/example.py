#!/usr/bin/env python3
"""
UnrealServer Python WebSocket Client Example

Example usage of the WebSocket client with event handling.
"""

import asyncio
import logging
from typing import Dict, Any

from .client import WebSocketClient, WebSocketConfig
from .events import SocketEvent, EventType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_event_handler(event: str, data: Dict[str, Any]) -> None:
    """
    Example event handler for WebSocket events.
    
    Args:
        event: Event name
        data: Event data
    """
    logger.info(f"📨 Received event: {event}")
    logger.info(f"📄 Data: {data}")
    
    # Handle specific events
    if event == SocketEvent.PARSER_REGISTRATION:
        logger.info("🔧 Parser registration event received")
    elif event == SocketEvent.HEALTH_STATUS:
        logger.info("💚 Health status update received")
    elif event == SocketEvent.COMMAND_RESPONSE:
        logger.info("📋 Command response received")


async def example_connection_handler(client: WebSocketClient) -> None:
    """
    Example connection event handler.
    
    Args:
        client: WebSocket client instance
    """
    logger.info("🔌 Connected to UnrealServer WebSocket server")
    
    # Send a test message
    await client.emit(SocketEvent.PING, {"timestamp": "2024-01-01T00:00:00Z"})


async def example_disconnect_handler(client: WebSocketClient) -> None:
    """
    Example disconnect event handler.
    
    Args:
        client: WebSocket client instance
    """
    logger.info("🔌 Disconnected from UnrealServer WebSocket server")


async def main():
    """Main example function."""
    
    # Configuration
    config = WebSocketConfig(
        url="ws://localhost:8000",  # Default server URL
        auto_connect=True,
        reconnection_attempts=5,
        reconnection_delay=2.0,
        timeout=10.0,
        auth={
            "api_key": "your-api-key-here",
            "developer_id": "your-developer-id"
        }
    )
    
    # Create client
    client = WebSocketClient(config)
    
    # Register event handlers
    client.on_event(example_event_handler)
    client.on_connect(example_connection_handler)
    client.on_disconnect(example_disconnect_handler)
    
    try:
        logger.info("🚀 Starting UnrealServer WebSocket client example")
        
        # Connect to server
        await client.connect()
        
        # Keep connection alive and handle events
        logger.info("⏳ Listening for events... Press Ctrl+C to stop")
        
        # Example: Send some test events
        await asyncio.sleep(2)
        
        # Send parser registration
        await client.emit(SocketEvent.PARSER_REGISTRATION, {
            "parser_id": "example-parser-001",
            "name": "Example Parser",
            "version": "1.0.0",
            "capabilities": ["parsing", "validation"]
        })
        
        await asyncio.sleep(2)
        
        # Send health check
        await client.emit(SocketEvent.HEALTH_STATUS, {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z"
        })
        
        # Keep running
        while client.connected:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        # Cleanup
        await client.disconnect()
        logger.info("✅ Example completed")


if __name__ == "__main__":
    """Run the example."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Example interrupted by user")
    except Exception as e:
        print(f"💥 Example failed: {e}")