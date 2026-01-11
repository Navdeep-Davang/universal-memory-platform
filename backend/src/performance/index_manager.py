import logging
from typing import List, Dict, Any, Optional
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

logger = logging.getLogger(__name__)

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
        logger.info(f"Tuning HNSW index for {label}({property_name})...")
        
        # In Memgraph, HNSW parameters are often set during creation.
        # If the index exists, we might need to drop and recreate it to change parameters.
        
        drop_query = f"DROP INDEX ON :{label}({property_name});"
        create_query = (
            f"CREATE INDEX ON :{label}({property_name}) "
            f"TYPE VECTOR "
            f"PARAMS {{ m: {m}, ef_construction: {ef_construction} }};"
        )
        
        try:
            # We try to drop if exists (ignore error if not exists)
            try:
                self.adapter.run_query(drop_query)
            except:
                pass
                
            self.adapter.run_query(create_query)
            logger.info("HNSW index tuned successfully.")
        except Exception as e:
            logger.error(f"Failed to tune HNSW index: {e}")

    def optimize_fts_index(self, label: str = "Experience", properties: List[str] = ["content"]):
        """
        Optimizes Full-Text Search index.
        """
        logger.info(f"Optimizing FTS index for {label} properties {properties}...")
        
        # Memgraph FTS (text.index) optimization usually involves ensuring 
        # it's correctly built on the right properties.
        
        props_str = ", ".join([f"'{p}'" for p in properties])
        query = f"CALL text.index.create('{label}', [{props_str}]);"
        
        try:
            self.adapter.run_query(query)
            logger.info("FTS index created/optimized.")
        except Exception as e:
            # If already exists, we might want to rebuild or just log
            logger.debug(f"FTS index creation info: {e}")

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

