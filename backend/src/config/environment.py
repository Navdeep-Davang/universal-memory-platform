from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # API
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Memgraph
    MEMGRAPH_HOST: str = "localhost"
    MEMGRAPH_PORT: int = 7687
    MEMGRAPH_USERNAME: Optional[str] = None
    MEMGRAPH_PASSWORD: Optional[str] = None

    # Cognitive
    DEFAULT_RECALL_DEPTH: int = 3
    DEFAULT_RECALL_BREADTH: int = 50

    # Ingestion & Infrastructure
    USE_OPENAI_EMBEDDING: bool = True
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    OPENAI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    API_KEY: str = "dev-key-123"  # Default for development
    RATE_LIMIT_PER_MINUTE: int = 60

    # GCP
    GCP_PROJECT_ID: Optional[str] = None
    GCP_LOCATION: str = "us-central1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

