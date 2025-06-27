from fastapi import HTTPException, Depends
import logging
from typing import AsyncGenerator

from neo4j import AsyncDriver
from qdrant_client import QdrantClient
import redis

logger = logging.getLogger(__name__)

# Global connection instances (initialized in lifespan in main.py)
neo4j_driver: AsyncDriver | None = None
qdrant_client: QdrantClient | None = None
redis_client: redis.Redis | None = None

async def get_neo4j_driver() -> AsyncGenerator[AsyncDriver, None]:
    """Dependency that provides a Neo4j driver instance."""
    if neo4j_driver is None:
        raise HTTPException(status_code=500, detail="Neo4j driver not initialized")
    yield neo4j_driver

async def get_qdrant_client() -> AsyncGenerator[QdrantClient, None]:
    """Dependency that provides a Qdrant client instance."""
    if qdrant_client is None:
        raise HTTPException(status_code=500, detail="Qdrant client not initialized")
    yield qdrant_client

async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    """Dependency that provides a Redis client instance."""
    if redis_client is None:
        raise HTTPException(status_code=500, detail="Redis client not initialized")
    yield redis_client

async def check_neo4j_connection(driver: AsyncDriver = Depends(get_neo4j_driver)):
    try:
        await driver.verify_connectivity()
        return {"status": "connected"}
    except Exception as e:
        logger.error(f"Neo4j connection failed: {e}")
        raise HTTPException(status_code=500, detail="Neo4j connection failed")

async def check_qdrant_connection(client: QdrantClient = Depends(get_qdrant_client)):
    try:
        client.get_collections() # A simple operation to check connectivity
        return {"status": "connected"}
    except Exception as e:
        logger.error(f"Qdrant connection failed: {e}")
        raise HTTPException(status_code=500, detail="Qdrant connection failed")

async def check_redis_connection(client: redis.Redis = Depends(get_redis_client)):
    try:
        client.ping()
        return {"status": "connected"}
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise HTTPException(status_code=500, detail="Redis connection failed")
