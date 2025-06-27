import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from neo4j import GraphDatabase
from qdrant_client import QdrantClient
import redis

from src.config import settings

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Neo4j GraphRAG API",
    description="API for Neo4j GraphRAG application with seamless local-to-production setup.",
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
)

# Add TrustedHostMiddleware for security
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"]) # Adjust in production

# Configure CORS
origins = [settings.FRONTEND_DOMAIN] if settings.FRONTEND_DOMAIN else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to check database connections (example, implement actual checks)
async def check_neo4j_connection():
    try:
        driver = GraphDatabase.driver(settings.NEO4J_URL, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))
        await driver.verify_connectivity()
        await driver.close()
        return {"status": "connected"}
    except Exception as e:
        logger.error(f"Neo4j connection failed: {e}")
        raise HTTPException(status_code=500, detail="Neo4j connection failed")

async def check_qdrant_connection():
    try:
        client = QdrantClient(host=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        client.get_collections()
        return {"status": "connected"}
    except Exception as e:
        logger.error(f"Qdrant connection failed: {e}")
        raise HTTPException(status_code=500, detail="Qdrant connection failed")

async def check_redis_connection():
    try:
        client = redis.from_url(settings.REDIS_URL)
        client.ping()
        return {"status": "connected"}
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise HTTPException(status_code=500, detail="Redis connection failed")

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



@app.get("/health")
def health_check():
    return {"status": "healthy"}

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