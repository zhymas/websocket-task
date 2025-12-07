from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect

from src.services.redis.dependencies.dependencies import get_redis_service
from src.services.redis.redis_service import RedisService


websocket_router = APIRouter()


@websocket_router.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    redis_service: RedisService = Depends(get_redis_service)
):
    try:
        await websocket.accept()

        client_id = str(uuid4())

        await websocket.send_text(f"Welcome to the websocket! Your client ID is: {client_id}")

        await redis_service.set_value(f"client_id:{client_id}", client_id)

        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        await redis_service.delete_value(f"client_id:{client_id}")
        print(f"Client {client_id} disconnected")