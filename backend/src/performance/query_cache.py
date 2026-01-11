import hashlib
import json
from typing import List, Optional, Dict, Any
from loguru import logger

from src.storage.adapters.cache_adapter import CacheAdapter
from src.models.memory_result import MemoryResult

class QueryCache:
    """
    Caches query results in Redis to hit the <300ms p95 target for frequent queries.
    """
    
    def __init__(self, cache_adapter: Optional[CacheAdapter] = None):
        # Use provided adapter or create a new one with default settings
        self.cache = cache_adapter or CacheAdapter()

    def _generate_query_key(
        self, 
        query: str, 
        agent_id: str, 
        limit: int, 
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates a deterministic cache key based on query parameters.
        """
        context = {
            "query": query,
            "agent_id": agent_id,
            "limit": limit,
            "metadata_filter": metadata_filter or {}
        }
        # sort_keys=True ensures the same dictionary produces the same JSON string
        context_json = json.dumps(context, sort_keys=True)
        hash_val = hashlib.sha256(context_json.encode()).hexdigest()
        return f"recall_cache:{hash_val}"

    def get_results(
        self, 
        query: str, 
        agent_id: str, 
        limit: int, 
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Optional[List[MemoryResult]]:
        """
        Try to retrieve results from the Redis cache.
        """
        key = self._generate_query_key(query, agent_id, limit, metadata_filter)
        cached_data = self.cache.get(key)
        
        if cached_data and isinstance(cached_data, list):
            logger.info(f"Query Cache: HIT for query: '{query[:30]}...'")
            try:
                return [MemoryResult(**res) for res in cached_data]
            except Exception as e:
                logger.error(f"Query Cache: Error deserializing cached results: {e}")
                return None
                
        logger.debug(f"Query Cache: MISS for query: '{query[:30]}...'")
        return None

    def set_results(
        self, 
        query: str, 
        agent_id: str, 
        limit: int, 
        results: List[MemoryResult], 
        metadata_filter: Optional[Dict[str, Any]] = None,
        ttl: int = 300 # Default 5 minutes
    ):
        """
        Store query results in the Redis cache.
        """
        key = self._generate_query_key(query, agent_id, limit, metadata_filter)
        try:
            # Convert MemoryResult objects to dicts for storage
            results_dict = [res.model_dump() for res in results]
            self.cache.set(key, results_dict, ttl=ttl)
            logger.debug(f"Query Cache: SET results for query: '{query[:30]}...' (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Query Cache: Failed to cache results: {e}")

