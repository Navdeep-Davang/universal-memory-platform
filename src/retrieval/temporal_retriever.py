from typing import List, Optional
from datetime import datetime, timedelta
from src.storage.adapters.graph_db_adapter import GraphDBAdapter
from src.models.memory_result import MemoryResult
from src.retrieval.utils import format_memory_result

class TemporalRetriever:
    """
    Retriever for accessing memories based on time and recency.
    """
    
    def __init__(self, adapter: GraphDBAdapter):
        self.adapter = adapter

    def get_recent_memories(
        self, 
        agent_id: str, 
        limit: int = 10,
        hours: Optional[int] = None
    ) -> List[MemoryResult]:
        """
        Retrieve the most recent memories for an agent.
        
        Args:
            agent_id: The ID of the agent.
            limit: Maximum number of memories to return.
            hours: Optional time window in hours to look back.
            
        Returns:
            A list of MemoryResult objects sorted by recency.
        """
        cypher = (
            "MATCH (n:Experience {agent_id: $agent_id}) "
        )
        
        params = {
            "agent_id": agent_id,
            "limit": limit
        }
        
        if hours:
            # Memgraph/Neo4j temporal types or epoch comparison
            # Assuming created_at is stored in a way that supports comparison
            # We'll use datetime objects which the driver handles
            since = datetime.utcnow() - timedelta(hours=hours)
            cypher += "WHERE n.created_at >= $since "
            params["since"] = since
            
        cypher += "RETURN n ORDER BY n.created_at DESC LIMIT $limit"
        
        results = self.adapter.run_query(cypher, params)
        
        memory_results = []
        for res in results:
            # res structure: {"n": {...}}
            memory_results.append(
                format_memory_result(
                    record=res, 
                    score=1.0, # Recency-based results are usually binary relevance
                    layer=res["n"].get("memory_type", "episodic")
                )
            )
            
        return memory_results

    def get_memories_in_range(
        self,
        agent_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 20
    ) -> List[MemoryResult]:
        """
        Retrieve memories within a specific time range.
        """
        cypher = (
            "MATCH (n:Experience {agent_id: $agent_id}) "
            "WHERE n.created_at >= $start_date AND n.created_at <= $end_date "
            "RETURN n ORDER BY n.created_at DESC LIMIT $limit"
        )
        
        params = {
            "agent_id": agent_id,
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit
        }
        
        results = self.adapter.run_query(cypher, params)
        
        return [format_memory_result(res, score=1.0) for res in results]

