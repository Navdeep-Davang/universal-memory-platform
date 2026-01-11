import os
import sys
from loguru import logger

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.config.environment import settings
from src.storage.adapters.graph_db_adapter import GraphDBAdapter
from src.performance.index_manager import PerformanceIndexManager

def setup_database():
    """
    Setup script to initialize Memgraph with required indexes and procedures.
    """
    logger.info("Starting Database Setup...")
    
    # 1. Initialize Adapter
    db_adapter = GraphDBAdapter(
        uri=f"bolt://{settings.MEMGRAPH_HOST}:{settings.MEMGRAPH_PORT}",
        user=settings.MEMGRAPH_USERNAME,
        password=settings.MEMGRAPH_PASSWORD
    )
    
    try:
        # 2. Connect and Initialize (Load modules)
        db_adapter.connect()
        db_adapter.initialize_database()
        
        # 3. Create Indexes using PerformanceIndexManager
        index_manager = PerformanceIndexManager(db_adapter)
        
        logger.info("Creating HNSW (Vector) index for Experience nodes...")
        index_manager.tune_hnsw_index(label="Experience", property_name="embedding")
        
        logger.info("Creating Full-Text Search (FTS) index for Experience nodes...")
        index_manager.optimize_fts_index(label="Experience", properties=["content"])
        
        logger.info("Creating Full-Text Search (FTS) index for Entity nodes...")
        index_manager.optimize_fts_index(label="Entity", properties=["name"])
        
        logger.success("Database setup completed successfully.")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)
    finally:
        db_adapter.disconnect()

if __name__ == "__main__":
    setup_database()
