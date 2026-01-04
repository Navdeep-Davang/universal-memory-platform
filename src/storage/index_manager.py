import logging
from typing import List
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

logger = logging.getLogger(__name__)

class IndexManager:
    """
    Manager for defining and initializing indexes in Memgraph/Neo4j.
    """
    
    @staticmethod
    def get_memgraph_indexes() -> List[str]:
        """Returns a list of standard index creation queries for Memgraph."""
        return [
            "CREATE INDEX ON :Experience(id);",
            "CREATE INDEX ON :Experience(agent_id);",
            "CREATE INDEX ON :Experience(created_at);",
            "CREATE INDEX ON :Entity(name);",
        ]

    @staticmethod
    def get_vector_index_query(label: str = "Experience", property_name: str = "embedding") -> str:
        """
        Returns the query for creating a vector index (HNSW) in Memgraph.
        Note: Memgraph 2.15+ uses 'TYPE VECTOR' syntax.
        """
        return f"CREATE INDEX ON :{label}({property_name}) TYPE VECTOR;"

    @classmethod
    def initialize_all(cls, adapter: GraphDBAdapter):
        """
        Executes all index creation queries using the provided adapter.
        Handles cases where indexes might already exist.
        """
        logger.info("Initializing database indexes...")
        
        # Standard indexes
        for query in cls.get_memgraph_indexes():
            try:
                adapter.run_query(query)
                logger.info(f"Successfully executed: {query}")
            except Exception as e:
                # Common to ignore if index already exists
                logger.debug(f"Could not create index (may exist): {query}. Error: {e}")

        # Vector index
        vector_query = cls.get_vector_index_query()
        try:
            adapter.run_query(vector_query)
            logger.info(f"Successfully created vector index: {vector_query}")
        except Exception as e:
            logger.warning(f"Failed to create vector index: {vector_query}. Error: {e}")

if __name__ == "__main__":
    # Example usage (would require environment variables in a real scenario)
    # adapter = GraphDBAdapter("bolt://localhost:7687", "user", "pass")
    # IndexManager.initialize_all(adapter)
    pass

