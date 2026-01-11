from typing import List, Optional
from src.storage.adapters.graph_db_adapter import GraphDBAdapter
from src.models.memory_result import MemoryResult
from src.retrieval.utils import format_memory_result

class SemanticRetriever:
    """
    Retriever for performing vector-based semantic search against Memgraph.
    """
    
    def __init__(self, adapter: GraphDBAdapter):
        self.adapter = adapter

    def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5, 
        agent_id: Optional[str] = None,
        memory_type: Optional[str] = None
    ) -> List[MemoryResult]:
        """
        Perform a semantic search using Memgraph's vector index.
        
        Args:
            query_embedding: The vector embedding of the query.
            top_k: Number of results to return.
            agent_id: Optional filter for a specific agent.
            memory_type: Optional filter for memory type (episodic, semantic, etc.).
            
        Returns:
            A list of MemoryResult objects.
        """
        # Base query using Memgraph's vector.search
        # Syntax: CALL vector.search(label, property, query_vector, top_k) YIELD node, similarity
        
        # We start with the vector search
        cypher = (
            "CALL vector.search('Experience', 'embedding', $embedding, $top_k) "
            "YIELD node, similarity "
        )
        
        params = {
            "embedding": query_embedding,
            "top_k": top_k
        }
        
        # Add filtering logic after the vector search
        filters = []
        if agent_id:
            filters.append("node.agent_id = $agent_id")
            params["agent_id"] = agent_id
        if memory_type:
            filters.append("node.memory_type = $memory_type")
            params["memory_type"] = memory_type
            
        if filters:
            cypher += "WHERE " + " AND ".join(filters) + " "
            
        cypher += "RETURN node, similarity ORDER BY similarity DESC"
        
        results = self.adapter.run_query(cypher, params)
        
        memory_results = []
        for res in results:
            # res structure: {"node": {...}, "similarity": 0.95}
            memory_results.append(
                format_memory_result(
                    record={"n": res["node"]}, 
                    score=res["similarity"], 
                    layer=res["node"].get("memory_type", "semantic")
                )
            )
            
        return memory_results

