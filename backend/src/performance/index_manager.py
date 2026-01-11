from loguru import logger
from typing import List, Dict, Any, Optional
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

class PerformanceIndexManager:
    """
    Advanced index manager for performance tuning of Memgraph/Neo4j.
    Handles HNSW (vector) and FTS (full-text search) optimizations.
    """
    
    def __init__(self, adapter: GraphDBAdapter):
        self.adapter = adapter

    def tune_hnsw_index(
        self, 
        label: str = "Experience", 
        property_name: str = "embedding",
        m: int = 16, 
        ef_construction: int = 200
    ):
        """
        Tuning HNSW index parameters for better vector search performance.
        M: Max number of outgoing connections in the graph.
        ef_construction: Size of the dynamic candidate list during index building.
        """
        index_name = f"idx_{label}_{property_name}"
        logger.info(f"Tuning HNSW index {index_name} for {label}({property_name})...")
        
        # 1. Drop existing if any
        try:
            self.adapter.run_query(f"DROP VECTOR INDEX {index_name};")
        except:
            pass
            
        # 2. Create using Native Cypher command (Memgraph v3.7+)
        # We assume 1536 dimensions for text-embedding-3-small
        # Memgraph v3.7 might require at least one node to exist or be created for some vector index configurations
        create_query = (
            f"CREATE VECTOR INDEX {index_name} "
            f"ON :{label}({property_name}) "
            f'WITH CONFIG {{"dimension": 1536, "metric": "cos", "capacity": 1000, "scalar_kind": "f32"}};'
        )
        
        try:
            # Optional: Create a temporary node to ensure the label/property exists if graph is empty
            # Generating a list of zeros for the embedding
            dummy_embedding = [0.0] * 1536
            self.adapter.run_query(
                f"CREATE (:{label} {{ {property_name}: $emb }});", 
                {"emb": dummy_embedding}
            )
            self.adapter.run_query(create_query)
            # Delete the temporary node after index creation
            self.adapter.run_query(f"MATCH (n:{label}) WHERE n.{property_name} = $emb DELETE n;", {"emb": dummy_embedding})
            logger.info(f"HNSW index {index_name} created successfully.")
        except Exception as e:
            logger.error(f"Failed to create HNSW index: {e}")

    def optimize_fts_index(self, label: str = "Experience", properties: List[str] = ["content"]):
        """
        Optimizes Full-Text Search index using Native Cypher command.
        """
        for prop in properties:
            index_name = f"idx_{label}_{prop}"
            logger.info(f"Optimizing FTS index {index_name} for {label}.{prop}...")
            
            # 1. Drop existing if any
            try:
                self.adapter.run_query(f"DROP TEXT INDEX {index_name};")
            except:
                pass

            # 2. Create using Native Cypher command
            query = f"CREATE TEXT INDEX {index_name} ON :{label}({prop});"
            
            try:
                self.adapter.run_query(query)
                logger.info(f"FTS index {index_name} created successfully.")
            except Exception as e:
                logger.error(f"FTS index creation failed: {e}")

    def get_index_health(self) -> List[Dict[str, Any]]:
        """Checks the status and health of all database indexes."""
        # Memgraph query for index status
        query = "SHOW INDEX INFO;"
        try:
            return self.adapter.run_query(query)
        except Exception as e:
            logger.error(f"Failed to get index info: {e}")
            return []

    def verify_hnsw_ready(self, label: str = "Experience") -> bool:
        """Verifies if the HNSW index is fully built and ready for search."""
        index_info = self.get_index_health()
        for idx in index_info:
            if idx.get("label") == label and idx.get("type") == "vector":
                # Check status if available in driver output
                return idx.get("status") == "READY" or idx.get("state") == "ONLINE"
        return False

