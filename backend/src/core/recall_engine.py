import asyncio
from typing import List, Optional
from loguru import logger

from src.models.memory_result import MemoryResult
from src.retrieval.semantic_retriever import SemanticRetriever
from src.retrieval.context_retriever import ContextRetriever
from src.retrieval.temporal_retriever import TemporalRetriever
from src.retrieval.graph_retriever import GraphRetriever

class RecallEngine:
    """
    Orchestrates the retrieval of memories from multiple paths concurrently.
    Launched retrieval paths include semantic, context (FTS), temporal, and graph.
    """
    
    def __init__(
        self,
        semantic_retriever: SemanticRetriever,
        context_retriever: ContextRetriever,
        temporal_retriever: TemporalRetriever,
        graph_retriever: GraphRetriever
    ):
        self.semantic = semantic_retriever
        self.context = context_retriever
        self.temporal = temporal_retriever
        self.graph = graph_retriever

    async def recall(
        self,
        query: str,
        query_embedding: List[float],
        agent_id: str,
        entity_names: Optional[List[str]] = None,
        limit: int = 10,
        timeout: float = 2.0
    ) -> List[MemoryResult]:
        """
        Execute concurrent retrieval paths and merge results.
        
        Args:
            query: The raw text query.
            query_embedding: The vector embedding of the query.
            agent_id: The ID of the agent performing the recall.
            entity_names: Optional list of entities extracted from the query for graph traversal.
            limit: Maximum results to retrieve per path.
            timeout: Global timeout for all retrieval paths in seconds.
            
        Returns:
            A list of unique MemoryResult objects.
        """
        logger.info(f"Recall Engine: Starting retrieval for agent {agent_id} with query: '{query[:50]}...'")
        
        # Define tasks for concurrent execution
        tasks = [
            self._safe_retrieve("semantic", self.semantic.search, query_embedding, limit, agent_id),
            self._safe_retrieve("context", self.context.search, query, limit, agent_id),
            self._safe_retrieve("temporal", self.temporal.get_recent_memories, agent_id, limit)
        ]
        
        # Add graph retrieval task if entities are provided
        if entity_names:
            logger.debug(f"Recall Engine: Adding graph retrieval task for entities: {entity_names}")
            tasks.append(
                self._safe_retrieve("graph", self.graph.retrieve_by_entities, entity_names, agent_id=agent_id)
            )
        
        try:
            # Run all retrieval paths concurrently
            # We use wait_for to enforce a hard global timeout
            results_nested = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
            
            # Flatten results and deduplicate by ID
            merged_results = {}
            for sub_results in results_nested:
                if not sub_results:
                    continue
                for res in sub_results:
                    if res.id not in merged_results:
                        merged_results[res.id] = res
                    else:
                        # If already exists, keep the one with higher relevance score
                        if res.score > merged_results[res.id].score:
                            merged_results[res.id] = res
            
            final_results = list(merged_results.values())
            logger.info(f"Recall Engine: Retrieval complete. Found {len(final_results)} unique memories.")
            return final_results
            
        except asyncio.TimeoutError:
            logger.warning(f"Recall Engine: Global timeout of {timeout}s reached. Returning partial results.")
            return []
        except Exception as e:
            logger.error(f"Recall Engine: Unexpected error during parallel retrieval: {e}")
            return []

    async def _safe_retrieve(self, name: str, func, *args, **kwargs) -> List[MemoryResult]:
        """
        Execute a single retrieval path and handle errors to prevent one path from 
        failing the entire recall operation.
        """
        try:
            logger.debug(f"Recall Engine: Launching {name} retrieval path...")
            # Use to_thread for synchronous retriever methods to avoid blocking the event loop
            return await asyncio.to_thread(func, *args, **kwargs)
        except Exception as e:
            logger.error(f"Recall Engine: Error in {name} retrieval path: {e}")
            return []
