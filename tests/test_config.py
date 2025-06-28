import os
from src.config import Settings
from pydantic_settings import SettingsConfigDict


def test_default_settings(monkeypatch):
    # Purpose: Verify that the Settings class loads default values correctly
    # when no environment variables or .env files are present.

    # Temporarily override model_config to prevent pydantic-settings from loading any .env files.
    # This ensures that only actual environment variables (or their absence) are considered.
    monkeypatch.setattr(
        Settings, "model_config", SettingsConfigDict(env_file=None, extra="ignore")
    )

    # Store original environment variables and clear relevant ones for this test.
    # This isolates the test from external environment configurations.
    original_env = os.environ.copy()
    for key in [
        "ENVIRONMENT",
        "LOG_LEVEL",
        "FRONTEND_DOMAIN",
        "NEO4J_URL",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "REDIS_URL",
    ]:
        if key in os.environ:
            del os.environ[key]

    # Instantiate Settings and assert that all values match their defined defaults.
    settings = Settings()
    assert settings.ENVIRONMENT == "development"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.FRONTEND_DOMAIN is None
    assert settings.NEO4J_URL == "neo4j://neo4j:7687"
    assert settings.NEO4J_USERNAME == "neo4j"
    assert settings.NEO4J_PASSWORD == "password"
    assert settings.QDRANT_URL == "http://qdrant:6333"
    assert settings.QDRANT_API_KEY is None
    assert settings.REDIS_URL == "redis://redis:6379"

    # Restore original environment variables after the test.
    os.environ.clear()
    os.environ.update(original_env)


def test_environment_variable_override(monkeypatch):
    # Purpose: Verify that environment variables correctly override default settings.

    # Temporarily override model_config to prevent .env loading, focusing only on env vars.
    monkeypatch.setattr(
        Settings, "model_config", SettingsConfigDict(env_file=None, extra="ignore")
    )

    # Set specific environment variables using monkeypatch.setenv.
    # This ensures these variables are set only for the duration of this test.
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("FRONTEND_DOMAIN", "https://prod.example.com")
    monkeypatch.setenv("NEO4J_URL", "neo4j+s://prod-neo4j:7687")
    monkeypatch.setenv("NEO4J_USERNAME", "prod_user")
    monkeypatch.setenv(
        "NEO4J_PASSWORD", "some_prod_password"
    )  # Using generic string for sensitive data
    monkeypatch.setenv("QDRANT_URL", "https://prod-qdrant.com")
    monkeypatch.setenv(
        "QDRANT_API_KEY", "some_prod_api_key"
    )  # Using generic string for sensitive data
    monkeypatch.setenv("REDIS_URL", "redis://prod-redis:6379")

    # Instantiate Settings and assert that values reflect the overridden environment variables.
    settings = Settings()
    assert settings.ENVIRONMENT == "production"
    assert settings.LOG_LEVEL == "DEBUG"
    assert settings.FRONTEND_DOMAIN == "https://prod.example.com"
    assert settings.NEO4J_URL == "neo4j+s://prod-neo4j:7687"
    assert settings.NEO4J_USERNAME == "prod_user"
    assert settings.NEO4J_PASSWORD == "some_prod_password"
    assert settings.QDRANT_URL == "https://prod-qdrant.com"
    assert settings.QDRANT_API_KEY == "some_prod_api_key"
    assert settings.REDIS_URL == "redis://prod-redis:6379"


def test_env_file_override(tmp_path, monkeypatch):
    # Purpose: Verify that settings are correctly loaded from a .env file,
    # and that .env values take precedence over defaults (but not over env vars).

    # Create a temporary .env file with test-specific content.
    # Using generic strings for sensitive fields to avoid exposing real data.
    env_content = """
    ENVIRONMENT=staging
    LOG_LEVEL=WARNING
    FRONTEND_DOMAIN=http://staging.example.com
    NEO4J_URL=neo4j://staging-neo4j:7687
    NEO4J_USERNAME=staging_user
    NEO4J_PASSWORD=some_staging_password
    QDRANT_URL=http://staging-qdrant:6333
    QDRANT_API_KEY=some_staging_api_key
    REDIS_URL=redis://staging-redis:6379
    """
    env_file = tmp_path / ".env"
    env_file.write_text(env_content)

    # Store original environment variables and clear relevant ones.
    # This ensures the test relies solely on the temporary .env file for these settings.
    original_env = os.environ.copy()
    for key in [
        "ENVIRONMENT",
        "LOG_LEVEL",
        "FRONTEND_DOMAIN",
        "NEO4J_URL",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "REDIS_URL",
    ]:
        if key in os.environ:
            del os.environ[key]

    # Change the current working directory to the temporary path.
    # This is crucial because pydantic-settings looks for .env files in the current directory.
    monkeypatch.chdir(tmp_path)

    # Instantiate Settings and assert that values reflect the .env file content.
    settings = Settings()
    assert settings.ENVIRONMENT == "staging"
    assert settings.LOG_LEVEL == "WARNING"
    assert settings.FRONTEND_DOMAIN == "http://staging.example.com"
    assert settings.NEO4J_URL == "neo4j://staging-neo4j:7687"
    assert settings.NEO4J_USERNAME == "staging_user"
    assert settings.NEO4J_PASSWORD == "some_staging_password"
    assert settings.QDRANT_URL == "http://staging-qdrant:6333"
    assert settings.QDRANT_API_KEY == "some_staging_api_key"
    assert settings.REDIS_URL == "redis://staging-redis:6379"

    # Restore original environment variables after the test.
    os.environ.clear()
    os.environ.update(original_env)
