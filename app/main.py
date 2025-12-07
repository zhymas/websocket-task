from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse

from src.routers.websockets import websocket_router
from src.services.redis.dependencies.dependencies import get_redis_service
from src.services.redis.redis_service import RedisService


app = FastAPI(
    title="Websocket API", version="1.0.0", description="A simple websocket API"
)


app.include_router(websocket_router, prefix="/ws", tags=["websockets"])


@app.get("/")
async def check_health():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})


@app.get("/redis-health")
async def check_redis_health(
    redis_service: RedisService = Depends(get_redis_service)
):
    return await redis_service.redis_client.ping()