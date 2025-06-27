from fastapi import HTTPException
import logging

from neo4j import GraphDatabase
from qdrant_client import QdrantClient

from src.config import settings

logger = logging.getLogger(__name__)

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
