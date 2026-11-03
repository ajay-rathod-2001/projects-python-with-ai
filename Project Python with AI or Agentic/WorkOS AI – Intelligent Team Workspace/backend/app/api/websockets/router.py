import json
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.api.websockets.connection_manager import ws_manager
from app.core.security import decode_token
from app.core.logging import logger

router = APIRouter()


@router.websocket("/ws/{workspace_id}")
async def workspace_websocket_endpoint(
    websocket: WebSocket,
    workspace_id: UUID,
    token: str = Query(...),
):
    """
    Real-time WebSocket endpoint:
    Authenticates token, joins workspace channel, and handles heartbeat presence.
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception as e:
        logger.warning(f"WebSocket auth failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    ws_id_str = str(workspace_id)
    await ws_manager.connect(ws_id_str, websocket)

    try:
        while True:
            raw_text = await websocket.receive_text()
            try:
                msg_data = json.loads(raw_text)
                event_type = msg_data.get("event")

                # Handle presence heartbeat or cursor updates
                if event_type == "presence.heartbeat":
                    await ws_manager.broadcast_to_workspace(
                        ws_id_str,
                        {
                            "event": "presence.update",
                            "data": {
                                "user_id": user_id,
                                "status": "online",
                                **msg_data.get("data", {}),
                            },
                        },
                    )
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(ws_id_str, websocket)
        await ws_manager.broadcast_to_workspace(
            ws_id_str,
            {
                "event": "presence.update",
                "data": {"user_id": user_id, "status": "offline"},
            },
        )

