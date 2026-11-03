import json
import asyncio
from typing import Dict, Set
from fastapi import WebSocket
from app.core.logging import logger
from app.database.redis import get_redis_client


class WebSocketConnectionManager:
    """Manages active WebSocket connections partitioned per workspace and bridges to Redis Pub/Sub."""

    def __init__(self):
        # Maps workspace_id -> set of active WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Tracks Redis subscriber tasks per workspace channel
        self.subscriber_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, workspace_id: str, websocket: WebSocket):
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = set()
            # Start background Redis channel subscriber for this workspace
            task = asyncio.create_task(self._listen_redis_channel(workspace_id))
            self.subscriber_tasks[workspace_id] = task

        self.active_connections[workspace_id].add(websocket)
        logger.info(f"WebSocket client connected to workspace {workspace_id}. Active: {len(self.active_connections[workspace_id])}")

    def disconnect(self, workspace_id: str, websocket: WebSocket):
        if workspace_id in self.active_connections:
            self.active_connections[workspace_id].discard(websocket)
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]
                # Cancel Redis subscriber task if no active clients remain
                task = self.subscriber_tasks.pop(workspace_id, None)
                if task:
                    task.cancel()
        logger.info(f"WebSocket client disconnected from workspace {workspace_id}.")

    async def broadcast_to_workspace(self, workspace_id: str, message: dict):
        """Direct local broadcast to all connected websockets in the workspace."""
        if workspace_id in self.active_connections:
            serialized = json.dumps(message)
            dead_sockets = set()
            for ws in self.active_connections[workspace_id]:
                try:
                    await ws.send_text(serialized)
                except Exception:
                    dead_sockets.add(ws)
            for dead in dead_sockets:
                self.disconnect(workspace_id, dead)

    async def _listen_redis_channel(self, workspace_id: str):
        """Background coroutine subscribing to Redis Pub/Sub channel for multi-instance sync."""
        client = await get_redis_client()
        if not client:
            return

        pubsub = client.pubsub()
        channel_name = f"workspace:{workspace_id}"
        await pubsub.subscribe(channel_name)

        try:
            async for message in pubsub.listen():
                if message and message.get("type") == "message":
                    payload_raw = message.get("data")
                    try:
                        data = json.loads(payload_raw)
                        await self.broadcast_to_workspace(workspace_id, data)
                    except Exception as e:
                        logger.error(f"Error forwarding Redis pub/sub message: {e}")
        except asyncio.CancelledError:
            await pubsub.unsubscribe(channel_name)
        except Exception as err:
            logger.error(f"Redis pub/sub subscriber error for workspace {workspace_id}: {err}")


ws_manager = WebSocketConnectionManager()

