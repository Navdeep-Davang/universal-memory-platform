from typing import List, Optional
from loguru import logger
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
        """
        memory_results = []
        exp_index = "idx_Experience_content"
        ent_index = "idx_Entity_name"
        
        # 1. Search in Experience content
        # Using search_all as search currently throws 'Unknown exception!' in Memgraph v3.7
        experience_cypher = (
            f"CALL text_search.search_all('{exp_index}', $keyword) "
            "YIELD node "
            "WITH node "
        )
        
        exp_params = {"keyword": keyword}
        
        if agent_id:
            experience_cypher += "WHERE node.agent_id = $agent_id "
            exp_params["agent_id"] = agent_id
            
        experience_cypher += "RETURN node"
        
        try:
            exp_results = self.adapter.run_query(experience_cypher, exp_params)
            for res in exp_results:
                memory_results.append(
                    format_memory_result(
                        record={"n": res["node"]},
                        score=1.0,  # search_all doesn't return score
                        layer=res["node"].get("memory_type", "episodic")
                    )
                )
        except Exception as e:
            logger.error(f"Error in Experience FTS search: {e}")
            
        # 2. Search in Entity names
        entity_cypher = (
            f"CALL text_search.search_all('{ent_index}', $keyword) "
            "YIELD node "
            "RETURN node"
        )
        
        try:
            ent_results = self.adapter.run_query(entity_cypher, {"keyword": keyword})
            for res in ent_results:
                node = res["node"]
                # Convert entity to a memory-like result
                node_id = str(node.get("id") or node.get("name") or "unknown")
                
                memory_results.append(
                    MemoryResult(
                        id=node_id,
                        content=f"Entity: {node.get('name', '')} (Type: {node.get('type', 'Unknown')})",
                        score=1.0, # search_all doesn't return score
                        layer="semantic",
                        paths_found=[],
                        confidence=float(node.get("importance_score", 0.5)),
                        provenance="graph_entity"
                    )
                )
        except Exception as e:
            logger.error(f"Error in Entity FTS search: {e}")
            
        # Sort combined results by score and limit
        memory_results.sort(key=lambda x: x.score, reverse=True)
        return memory_results[:top_k]

