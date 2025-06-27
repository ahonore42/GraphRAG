import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from neo4j import AsyncGraphDatabase
from qdrant_client import QdrantClient
import redis

from src.core.db.connections import (
    check_neo4j_connection,
    check_qdrant_connection,
    check_redis_connection,
)

from src.config import settings

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the application."""
    global neo4j_driver, qdrant_client, redis_client
    logger.info("Application startup: Initializing database connections...")
    try:
        # Initialize Neo4j Driver
        global neo4j_driver
        neo4j_driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URL, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
        await neo4j_driver.verify_connectivity()
        logger.info("Neo4j driver initialized and connected.")

        # Initialize Qdrant Client
        global qdrant_client
        qdrant_client = QdrantClient(
            url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY
        )
        qdrant_client.get_collections()  # Verify connection
        logger.info("Qdrant client initialized and connected.")

        # Initialize Redis Client
        global redis_client
        redis_client = redis.from_url(settings.REDIS_URL)
        redis_client.ping()  # Verify connection
        logger.info("Redis client initialized and connected.")

    except Exception as e:
        logger.error(f"Failed to initialize database connections: {e}")
        # Depending on your strategy, you might want to exit or raise here
        # For now, we'll let the app start but health checks will fail.

    yield

    logger.info("Application shutdown: Closing database connections...")
    if neo4j_driver:
        await neo4j_driver.close()
        logger.info("Neo4j driver closed.")
    if qdrant_client:
        # Qdrant client typically doesn't have a close method, but if it did, call it here.
        pass
    if redis_client:
        redis_client.close()
        logger.info("Redis client closed.")


app = FastAPI(
    title="Neo4j GraphRAG API",
    description="API for Neo4j GraphRAG application with seamless local-to-production setup.",
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# Add TrustedHostMiddleware for security
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Adjust in production

# Configure CORS
origins = [settings.FRONTEND_DOMAIN] if settings.FRONTEND_DOMAIN else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check(
    neo4j_status: dict = Depends(check_neo4j_connection),
    qdrant_status: dict = Depends(check_qdrant_connection),
    redis_status: dict = Depends(check_redis_connection),
):
    return {
        "status": "healthy",
        "dependencies": {
            "neo4j": neo4j_status,
            "qdrant": qdrant_status,
            "redis": redis_status,
        },
        "environment": settings.ENVIRONMENT,
        "log_level": settings.LOG_LEVEL,
    }


@app.get("/config")
async def get_config():
    return JSONResponse(content=settings.model_dump())


def main():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        workers=1 if settings.ENVIRONMENT == "development" else os.cpu_count() or 1,
    )


if __name__ == "__main__":
    logger.info(f"Starting application in {settings.ENVIRONMENT} mode...")
    main()
