from typing import List
from sentence_transformers import SentenceTransformer
from src.config.environment import settings
from loguru import logger

class EmbeddingAdapter:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        logger.info(f"Initializing EmbeddingAdapter with model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)

    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding for a single string."""
        logger.debug(f"Embedding text: {text[:50]}...")
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of strings."""
        logger.debug(f"Embedding batch of {len(texts)} texts")
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

