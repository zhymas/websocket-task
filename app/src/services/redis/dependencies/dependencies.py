from src.config.config import settings
from src.services.redis.redis_service import RedisService
from redis.asyncio import Redis


def get_redis_service() -> RedisService:
    redis_client = Redis(
        host=settings.redis_settings.host,
        port=settings.redis_settings.port,
        password=settings.redis_settings.password,
    )
    return RedisService(redis_client=redis_client)