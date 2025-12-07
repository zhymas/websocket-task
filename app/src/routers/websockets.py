from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.services.websocket.interfaces import IConnectionManager
from src.services.websocket.dependencies.dependencies import get_connection_manager


websocket_router = APIRouter()


@websocket_router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    manager: IConnectionManager = Depends(get_connection_manager),
):
    client = await manager.connect(websocket)
    await websocket.send_json(
        {
            "event": "connected",
            "connection_id": client.id,
            "connected_at": client.connected_at.isoformat(),
            "active_connections": manager.active_connection_count,
        }
    )
    try:
        while True:
            incoming = await websocket.receive_text()
            await websocket.send_json(
                {
                    "event": "message-received",
                    "message": incoming,
                    "echoed_at": datetime.now(timezone.utc).isoformat(),
                }
            )
    except WebSocketDisconnect:
        await manager.disconnect(client.id)
    except Exception:
        await manager.disconnect(client.id)
        raise