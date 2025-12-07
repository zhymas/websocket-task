from typing import Any
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status

from src.schema.broadcast import BroadcastPayload
from src.services.websocket.interfaces import IConnectionManager
from src.services.websocket.dependencies.dependencies import get_connection_manager


broadcast_router = APIRouter()


@broadcast_router.post(
    "/broadcast",
    status_code=status.HTTP_200_OK,
    summary="Broadcast a message to all connected WebSocket clients.",
)
async def broadcast_message(
    payload: BroadcastPayload,
    manager: IConnectionManager = Depends(get_connection_manager),
) -> dict[str, Any]:
    delivered = await manager.broadcast_json(
        {
            "event": "manual-broadcast",
            "message": payload.message,
            "sender": payload.sender or "api",
            "metadata": payload.metadata or {},
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return {
        "delivered_connections": delivered,
        "active_connections": manager.active_connection_count,
        "connection_ids": manager.connection_ids,
    }