from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.services.websocket.dependencies.dependencies import (
    get_notification_broadcaster,
    get_shutdown_guard,
)
from src.routers.broadcast import broadcast_router
from src.routers.websockets import websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    broadcaster = get_notification_broadcaster()
    shutdown_guard = get_shutdown_guard()

    broadcaster.start()
    yield
    await broadcaster.stop()
    await shutdown_guard.wait_for_shutdown()


app = FastAPI(
    title="Websocket API",
    version="1.0.0",
    description="A WebSocket API with graceful shutdown support",
    lifespan=lifespan,
)

# WEBSOCKETS ROUTER
app.include_router(websocket_router, prefix="/ws", tags=["websockets"])

# BROADCAST ROUTER
app.include_router(broadcast_router, prefix="/broadcast", tags=["broadcast"])


@app.get("/")
async def check_health():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})