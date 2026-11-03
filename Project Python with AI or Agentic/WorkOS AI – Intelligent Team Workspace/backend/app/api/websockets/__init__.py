"""Real-time WebSocket connection manager and routes."""
from app.api.websockets.connection_manager import ws_manager
from app.api.websockets.router import router as ws_router

__all__ = ["ws_manager", "ws_router"]

