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
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379/0"

    # GCP
    GCP_PROJECT_ID: Optional[str] = None
    GCP_LOCATION: str = "us-central1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

