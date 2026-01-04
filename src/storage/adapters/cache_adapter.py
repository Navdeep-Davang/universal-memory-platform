import json
import hashlib
from typing import Optional, List, Any
import redis
from src.config.environment import settings
from loguru import logger

class CacheAdapter:
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or settings.REDIS_URL
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            self.client.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis at {self.redis_url}: {e}. Caching will be disabled.")
            self.client = None

    def _generate_key(self, content: str, prefix: str = "emb") -> str:
        """Generate a unique key based on content hash."""
        hash_val = hashlib.sha256(content.encode()).hexdigest()
        return f"{prefix}:{hash_val}"

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Retrieve embedding from cache if it exists."""
        if not self.client:
            return None
        
        key = self._generate_key(text)
        try:
            cached = self.client.get(key)
            if cached:
                logger.debug(f"Cache hit for embedding: {key}")
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Error reading from Redis: {e}")
        
        return None

    def set_embedding(self, text: str, embedding: List[float], ttl: int = 3600 * 24):
        """Store embedding in cache with an optional TTL (default 24h)."""
        if not self.client:
            return
        
        key = self._generate_key(text)
        try:
            self.client.set(key, json.dumps(embedding), ex=ttl)
            logger.debug(f"Cached embedding: {key}")
        except Exception as e:
            logger.error(f"Error writing to Redis: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Generic get."""
        if not self.client:
            return None
        try:
            val = self.client.get(key)
            return json.loads(val) if val else None
        except:
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Generic set."""
        if not self.client:
            return
        try:
            self.client.set(key, json.dumps(value), ex=ttl)
        except Exception as e:
            logger.error(f"Error writing to Redis: {e}")

