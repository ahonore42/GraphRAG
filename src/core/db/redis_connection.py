from fastapi import HTTPException
import logging
import redis

from src.config import settings

logger = logging.getLogger(__name__)

async def check_redis_connection():
    try:
        client = redis.from_url(settings.REDIS_URL)
        client.ping()
        return {"status": "connected"}
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise HTTPException(status_code=500, detail="Redis connection failed")
