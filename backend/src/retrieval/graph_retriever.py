from loguru import logger
from typing import List, Optional
from src.storage.adapters.graph_db_adapter import GraphDBAdapter
from src.core.graph_engine import GraphEngine
from src.models.memory_result import MemoryResult
from src.retrieval.utils import format_memory_result

class GraphRetriever:
    """
    Retriever that uses graph traversal to find relevant memories 
    linked to entities mentioned in a query.
    """
    
    def __init__(self, adapter: GraphDBAdapter):
        self.adapter = adapter
        self.graph_engine = GraphEngine(adapter)

    def retrieve_by_entities(
        self, 
        entity_names: List[str], 
        k: int = 2, 
        fan_out_limit: int = 5,
        agent_id: Optional[str] = None
    ) -> List[MemoryResult]:
        """
        Retrieves memories (Experience nodes) by traversing the graph 
        from specific entities.
        
        Args:
            entity_names: List of entity names to start traversal from.
            k: Max hops for AKHLT.
            fan_out_limit: Fan-out limit for traversal.
            agent_id: Optional filter for memories belonging to a specific agent.
            
        Returns:
            A list of MemoryResult objects.
        """
        if not entity_names:
            return []

        # 1. Find the internal IDs for these entities
        entity_query = "MATCH (e:Entity) WHERE e.name IN $names RETURN e.id as id"
        entity_results = self.adapter.run_query(entity_query, {"names": entity_names})
        start_node_ids = [res["id"] for res in entity_results]

        if not start_node_ids:
            logger.debug(f"No entities found for names: {entity_names}")
            return []

        # 2. Perform AKHLT traversal
        traversal_results = self.graph_engine.adaptive_k_hop_traversal(
            start_node_ids=start_node_ids,
            k=k,
            fan_out_limit=fan_out_limit
        )

        # 3. Filter for Experience nodes and format into MemoryResult
        memory_results = []
        seen_ids = set()

        for res in traversal_results:
            node = res["neighbor"]
            # We only want to return memories (Experiences), not other entities
            # unless specifically requested. Usually, graph traversal finds 
            # related experiences.
            
            # Check labels - Neo4j/Memgraph driver might return labels in different ways 
            # depending on how the query was structured. If we used MATCH (n), 
            # 'neighbor' might be a Node object with .labels property.
            
            # Since run_query returns record.data(), 'neighbor' is a dict of properties.
            # We might need to adjust the query to return labels if they aren't implicit.
            
            # For now, we assume if it has 'content' and 'agent_id', it's an Experience.
            if "content" in node and "agent_id" in node:
                if agent_id and node["agent_id"] != agent_id:
                    continue
                
                node_id = node.get("id")
                if node_id in seen_ids:
                    continue
                
                seen_ids.add(node_id)
                
                # Format path information
                # res["r"] is the list of relationships in the path
                path_desc = " -> ".join([rel.get("rel_type", "RELATED") for rel in res.get("r", [])])
                
                mem_res = format_memory_result(
                    record={"n": node},
                    score=res.get("path_strength", 0.5),
                    layer="graph"
                )
                mem_res.paths_found = [path_desc]
                memory_results.append(mem_res)

        return memory_results

