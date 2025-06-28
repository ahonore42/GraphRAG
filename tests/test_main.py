from fastapi.testclient import TestClient
import pytest
from unittest.mock import AsyncMock, MagicMock


# This fixture is automatically used by all tests in this file (autouse=True).
# Its purpose is to mock the external database connections (Neo4j, Qdrant, Redis)
# so that tests can run without needing actual database instances.
# This ensures tests are fast, isolated, and reliable.
@pytest.fixture(autouse=True)
def mock_db_connections(monkeypatch):
    # Mock the AsyncGraphDatabase.driver constructor.
    # This prevents the application from trying to establish a real Neo4j connection.
    mock_neo4j_driver_instance = AsyncMock()
    mock_neo4j_driver_instance.verify_connectivity.return_value = (
        None  # Simulate successful connection verification
    )
    mock_neo4j_driver_instance.close.return_value = (
        None  # Simulate successful driver closure
    )
    monkeypatch.setattr(
        "neo4j.AsyncGraphDatabase.driver",
        MagicMock(return_value=mock_neo4j_driver_instance),
    )

    # Mock the QdrantClient constructor.
    # This prevents the application from trying to establish a real Qdrant connection.
    mock_qdrant_client_instance = MagicMock()
    mock_qdrant_client_instance.get_collections.return_value = (
        None  # Simulate a successful Qdrant operation
    )
    monkeypatch.setattr(
        "qdrant_client.QdrantClient",
        MagicMock(return_value=mock_qdrant_client_instance),
    )

    # Mock the redis.from_url constructor.
    # This prevents the application from trying to establish a real Redis connection.
    mock_redis_client_instance = MagicMock()
    mock_redis_client_instance.ping.return_value = (
        True  # Simulate a successful Redis ping
    )
    mock_redis_client_instance.close.return_value = (
        None  # Simulate successful client closure
    )
    monkeypatch.setattr(
        "redis.from_url", MagicMock(return_value=mock_redis_client_instance)
    )

    # Crucially, we set the global connection instances in src.core.db.connections
    # to our mock objects. This ensures that when the FastAPI app's lifespan function
    # (which initializes these globals) runs, it assigns our mocks, not real clients.
    # This is vital for the health check to pass with mocked dependencies.
    monkeypatch.setattr(
        "src.core.db.connections.neo4j_driver", mock_neo4j_driver_instance
    )
    monkeypatch.setattr(
        "src.core.db.connections.qdrant_client", mock_qdrant_client_instance
    )
    monkeypatch.setattr(
        "src.core.db.connections.redis_client", mock_redis_client_instance
    )


# This fixture provides a TestClient instance for making requests to the FastAPI app.
# It depends on mock_db_connections to ensure that database mocks are in place
# before the FastAPI app is initialized and its lifespan function runs.
@pytest.fixture(name="client")
def test_client(mock_db_connections):
    # Import the FastAPI app here to ensure it's initialized after mocks are applied.
    from src.main import app

    return TestClient(app)


# Test case for the /health endpoint.
# Purpose: Verify that the health endpoint returns a successful status (200 OK)
# and indicates that all its dependencies (Neo4j, Qdrant, Redis) are healthy,
# using mocked database connections.
def test_health_check(client):
    # Make a GET request to the /health endpoint.
    response = client.get("/health")

    # Assert that the HTTP status code is 200 (OK).
    assert response.status_code == 200

    # Assert that the overall status in the JSON response is "healthy".
    assert response.json()["status"] == "healthy"

    # Assert that the JSON response includes status for each expected dependency.
    assert "neo4j" in response.json()["dependencies"]
    assert "qdrant" in response.json()["dependencies"]
    assert "redis" in response.json()["dependencies"]
