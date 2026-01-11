from typing import List, Optional
from src.config.environment import settings
from loguru import logger
from openai import OpenAI

class EmbeddingAdapter:
    def __init__(self, model_name: str = None, use_openai: Optional[bool] = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.use_openai = use_openai if use_openai is not None else settings.USE_OPENAI_EMBEDDING

        if not self.use_openai:
            raise ValueError("Local embeddings are not supported. Please use OpenAI embeddings.")

        logger.info(f"Initializing EmbeddingAdapter with OpenAI model: {self.model_name}")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding for a single string."""
        logger.debug(f"Embedding text: {text[:50]}...")

        response = self.client.embeddings.create(
            input=[text],
            model=self.model_name
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of strings."""
        logger.debug(f"Embedding batch of {len(texts)} texts")

        response = self.client.embeddings.create(
            input=texts,
            model=self.model_name
        )
        return [item.embedding for item in response.data]

