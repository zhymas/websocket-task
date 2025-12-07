from redis.asyncio import Redis


class RedisService:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get_value(self, key: str) -> str:
        return await self.redis_client.get(key)

    async def set_value(self, key: str, value: str):
        await self.redis_client.set(key, value)

    async def delete_value(self, key: str):
        await self.redis_client.delete(key)