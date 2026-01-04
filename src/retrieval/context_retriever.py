from typing import List, Optional
from src.storage.adapters.graph_db_adapter import GraphDBAdapter
from src.models.memory_result import MemoryResult
from src.retrieval.utils import format_memory_result

class ContextRetriever:
    """
    Retriever for performing keyword-based full-text search (FTS) against Memgraph.
    """
    
    def __init__(self, adapter: GraphDBAdapter):
        self.adapter = adapter

    def search(
        self, 
        keyword: str, 
        top_k: int = 5,
        agent_id: Optional[str] = None
    ) -> List[MemoryResult]:
        """
        Perform a full-text search for keywords in experience content and entity names.
        
        Args:
            keyword: The search term or phrase.
            top_k: Number of results to return.
            agent_id: Optional filter for a specific agent.
            
        Returns:
            A combined list of MemoryResult objects from Experience and Entity matches.
        """
        memory_results = []
        
        # 1. Search in Experience content
        # CALL text.index.search(index_name, query, limit) YIELD node, score
        experience_cypher = (
            "CALL text.index.search('Experience', $keyword, $top_k) "
            "YIELD node, score "
        )
        
        exp_params = {"keyword": keyword, "top_k": top_k}
        
        if agent_id:
            experience_cypher += "WHERE node.agent_id = $agent_id "
            exp_params["agent_id"] = agent_id
            
        experience_cypher += "RETURN node, score"
        
        exp_results = self.adapter.run_query(experience_cypher, exp_params)
        for res in exp_results:
            memory_results.append(
                format_memory_result(
                    record={"n": res["node"]},
                    score=res["score"],
                    layer=res["node"].get("memory_type", "episodic")
                )
            )
            
        # 2. Search in Entity names (limited context)
        # Note: Entities don't have 'content' like Experience, but we can treat 
        # their name/type as content for retrieval purposes.
        entity_cypher = (
            "CALL text.index.search('Entity', $keyword, $top_k) "
            "YIELD node, score "
            "RETURN node, score"
        )
        
        ent_results = self.adapter.run_query(entity_cypher, {"keyword": keyword, "top_k": top_k})
        for res in ent_results:
            node = res["node"]
            # Convert entity to a memory-like result
            memory_results.append(
                MemoryResult(
                    id=str(node.get("id", "unknown")),
                    content=f"Entity: {node.get('name', '')} (Type: {node.get('type', 'Unknown')})",
                    score=float(res["score"]),
                    layer="semantic", # Entities are semantic knowledge
                    paths_found=[],
                    confidence=float(node.get("importance_score", 0.5)),
                    provenance="graph_entity"
                )
            )
            
        # Sort combined results by score and limit
        memory_results.sort(key=lambda x: x.score, reverse=True)
        return memory_results[:top_k]

