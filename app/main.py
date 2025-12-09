import asyncio
import uvicorn

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from src.services.websocket.dependencies.dependencies import (
    get_signal_handler,
)
from src.routers.broadcast import broadcast_router
from src.routers.websockets import websocket_router



app = FastAPI(
    title="Websocket API",
    version="1.0.0",
    description="A WebSocket API with graceful shutdown support"
)

# WEBSOCKETS ROUTER
app.include_router(websocket_router, prefix="/ws", tags=["websockets"])

# BROADCAST ROUTER
app.include_router(broadcast_router, prefix="/broadcast", tags=["broadcast"])


async def main():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    handler = get_signal_handler(server=server)
    handler.register_signal_handler()

    await server.serve()


@app.get("/")
async def check_health():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})


if __name__ == "__main__":
    asyncio.run(main())