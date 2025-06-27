from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    FRONTEND_DOMAIN: str | None = None

    # Database settings (example, adjust as needed)
    NEO4J_URL: str = "neo4j://neo4j:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_API_KEY: str | None = None

    REDIS_URL: str = "redis://redis:6379"


settings = Settings()
