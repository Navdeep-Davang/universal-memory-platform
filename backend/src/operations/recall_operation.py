import asyncio
from typing import List, Optional, Dict, Any
from loguru import logger

from src.core.recall_engine import RecallEngine
from src.ranking.fusion_ranker import FusionRanker
from src.storage.adapters.embedding_adapter import EmbeddingAdapter
from src.storage.adapters.graph_db_adapter import GraphDBAdapter
from src.storage.adapters.llm_adapter import LLMAdapter
from src.retrieval.semantic_retriever import SemanticRetriever
from src.retrieval.context_retriever import ContextRetriever
from src.retrieval.temporal_retriever import TemporalRetriever
from src.retrieval.graph_retriever import GraphRetriever
from src.config.environment import settings
from src.models.memory_result import MemoryResult
from src.performance.query_cache import QueryCache
from src.performance.latency_tracker import LatencyTracker

class RecallOperation:
    """
    Coordinates the end-to-end recall process:
    1. Query preprocessing (embedding generation & entity extraction)
    2. Multi-path retrieval via RecallEngine
    3. Result fusion and ranking
    """
    
    def __init__(self):
        # Initialize storage and embedding adapters
        self.db_adapter = GraphDBAdapter(
            uri=f"bolt://{settings.MEMGRAPH_HOST}:{settings.MEMGRAPH_PORT}",
            user=settings.MEMGRAPH_USERNAME,
            password=settings.MEMGRAPH_PASSWORD
        )
        self.embedding_adapter = EmbeddingAdapter()
        self.llm_adapter = LLMAdapter(provider=settings.LLM_PROVIDER, model=settings.LLM_MODEL)
        
        # Initialize specialized retrievers
        self.semantic = SemanticRetriever(self.db_adapter)
        self.context = ContextRetriever(self.db_adapter)
        self.temporal = TemporalRetriever(self.db_adapter)
        self.graph = GraphRetriever(self.db_adapter)
        
        # Initialize the engine and ranker
        self.engine = RecallEngine(
            semantic_retriever=self.semantic,
            context_retriever=self.context,
            temporal_retriever=self.temporal,
            graph_retriever=self.graph
        )
        self.ranker = FusionRanker()
        
        # Initialize query cache
        self.query_cache = QueryCache()

    async def execute(
        self,
        query: str,
        agent_id: str,
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
        entities: Optional[List[str]] = None
    ) -> List[MemoryResult]:
        """
        Execute the recall operation.
        
        Args:
            query: The user's search query.
            agent_id: The ID of the agent performing the search.
            limit: Total number of results to return.
            metadata_filter: Optional filters for memory metadata.
            entities: Pre-extracted entity names (optional).
            
        Returns:
            A list of ranked MemoryResult objects.
        """
        logger.info(f"Recall Operation: Starting for query: '{query[:50]}...'")
        tracker = LatencyTracker()
        
        try:
            with tracker.track("total_recall"):
                # 0. Check Query Cache
                with tracker.track("cache_lookup"):
                    cached_results = self.query_cache.get_results(query, agent_id, limit, metadata_filter)
                    if cached_results is not None:
                        return cached_results

                # 1. Query Preprocessing (Embedding & Entities)
                # Run concurrently to save time
                with tracker.track("preprocessing"):
                    logger.debug("Recall Operation: Generating query embedding")
                    embedding_task = asyncio.to_thread(self.embedding_adapter.embed_text, query)
                    
                    if entities:
                        logger.debug(f"Recall Operation: Using {len(entities)} provided entities")
                        query_embedding = await embedding_task
                        entity_names = entities
                    elif not settings.LITE_MODE:
                        logger.debug("Recall Operation: Extracting entities for graph search")
                        entity_task = self.llm_adapter.extract_entities(query)
                        query_embedding, raw_entities = await asyncio.gather(embedding_task, entity_task)
                        entity_names = [ent["name"] for ent in raw_entities] if raw_entities else []
                    else:
                        logger.debug("LITE_MODE active: skipping entity extraction")
                        query_embedding = await embedding_task
                        entity_names = []
                    
                    logger.debug(f"Recall Operation: Preprocessing complete. Entities: {len(entity_names)}")
                
                # 2. Parallel retrieval from multiple paths
                with tracker.track("multi_path_retrieval"):
                    logger.debug("Recall Operation: Launching recall engine")
                    raw_results = await self.engine.recall(
                        query=query,
                        query_embedding=query_embedding,
                        agent_id=agent_id,
                        entity_names=entity_names,
                        limit=limit * 2 # Retrieve more for better ranking pool
                    )
                
                if not raw_results:
                    logger.warning("Recall Operation: No memories found for the given query.")
                    return []
                
                # 3. Fusion and Ranking
                with tracker.track("fusion_and_ranking"):
                    logger.debug(f"Recall Operation: Ranking {len(raw_results)} results")
                    ranked_results = self.ranker.rank(raw_results, query=query)
                
                # 4. Final limit
                final_results = ranked_results[:limit]
                
                # 5. Cache Results
                with tracker.track("cache_update"):
                    self.query_cache.set_results(query, agent_id, limit, final_results, metadata_filter)
            
            report = tracker.get_formatted_report()
            logger.info(f"Recall Operation: Completed in {tracker.total_latency()*1000:.2f}ms. Stages: {report}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Recall Operation: Failed to execute recall: {e}")
            # In case of failure, return empty results instead of crashing
            return []
