from pydantic_settings import BaseSettings

class CognitiveSettings(BaseSettings):
    DEFAULT_RECALL_DEPTH: int = 3
    DEFAULT_RECALL_BREADTH: int = 50

    class Config:
        env_prefix = "COG_" # Example prefix if needed

cognitive_defaults = CognitiveSettings()

