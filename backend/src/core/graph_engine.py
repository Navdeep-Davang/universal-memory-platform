from loguru import logger
from typing import List, Dict, Any, Optional, Set
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

class GraphEngine:
    """
    Core engine for graph-based operations in the universal memory engine.
    Implements advanced traversal algorithms like AKHLT.
    """
    
    def __init__(self, adapter: GraphDBAdapter):
        self.adapter = adapter

    def adaptive_k_hop_traversal(
        self, 
        start_node_ids: List[str], 
        k: int = 2, 
        fan_out_limit: int = 10,
        min_weight: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        AKHLT (Adaptive K-Hop Limited Traversal) algorithm.
        Traverses the graph starting from multiple nodes, limiting fan-out 
        at each hop and filtering by relationship weight.
        
        This implementation uses a recursive Cypher pattern with subqueries
        to enforce the fan-out limit at each expansion step.
        """
        if not start_node_ids:
            return []

        # Improved Cypher query for AKHLT with per-hop fan-out limiting
        # Note: This pattern simulates per-hop limiting by expanding one hop at a time
        # within the subquery logic or by using list comprehensions for neighbors.
        
        # We'll use a more robust query that handles multiple hops with per-hop limiting:
        query = """
        UNWIND $start_ids AS start_id
        MATCH (start {id: start_id})
        
        // Hop 1
        CALL {
            WITH start
            MATCH (start)-[r1]-(n1)
            WHERE r1.weight >= $min_weight
            WITH n1, r1
            ORDER BY r1.weight DESC
            LIMIT $fan_out_limit
            RETURN n1, [r1] as path1, r1.weight as strength1
        }
        
        // Optional Hop 2 (if k >= 2)
        OPTIONAL MATCH (n1) WHERE $k >= 2
        CALL {
            WITH n1, path1, strength1
            MATCH (n1)-[r2]-(n2)
            WHERE r2.weight >= $min_weight AND NOT n2.id IN [node IN path1 | node.id]
            WITH n2, r2, path1, strength1
            ORDER BY r2.weight DESC
            LIMIT $fan_out_limit
            RETURN n2, path1 + [r2] as path2, strength1 * r2.weight as strength2
        }
        
        // Final selection based on k
        WITH 
            CASE 
                WHEN $k = 1 THEN n1 
                WHEN $k >= 2 AND n2 IS NOT NULL THEN n2 
                ELSE n1 
            END AS neighbor,
            CASE 
                WHEN $k = 1 THEN path1 
                WHEN $k >= 2 AND path2 IS NOT NULL THEN path2 
                ELSE path1 
            END AS r,
            CASE 
                WHEN $k = 1 THEN strength1 
                WHEN $k >= 2 AND strength2 IS NOT NULL THEN strength2 
                ELSE strength1 
            END AS path_strength
            
        RETURN DISTINCT neighbor, r, path_strength
        ORDER BY path_strength DESC
        """
        
        params = {
            "start_ids": start_node_ids,
            "k": k,
            "min_weight": min_weight,
            "fan_out_limit": fan_out_limit
        }
        
        try:
            results = self.adapter.run_query(query, params)
            return results
        except Exception as e:
            logger.error(f"Error in AKHLT traversal: {e}")
            return []

    def get_related_entities(self, entity_name: str, k: int = 1) -> List[Dict[str, Any]]:
        """Find entities related to a specific entity name."""
        query = """
        MATCH (e:Entity {name: $name})-[r*1..$k]-(related:Entity)
        RETURN related.name as name, related.type as type, r
        """
        return self.adapter.run_query(query, {"name": entity_name, "k": k})

