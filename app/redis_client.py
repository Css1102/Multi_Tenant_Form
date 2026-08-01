import redis
import os
import redis.asyncio as aioredis


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
sync_redis = redis.Redis.from_url(REDIS_URL, decode_responses=True)
async_redis = aioredis.from_url(REDIS_URL, decode_responses=True)