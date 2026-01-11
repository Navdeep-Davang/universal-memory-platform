from typing import Any, Dict, List, Optional, Union
from neo4j import GraphDatabase, Driver, Session
from loguru import logger
import time

class GraphDBAdapter:
    """
    Adapter for interacting with Graph Databases (Memgraph/Neo4j) using the Neo4j driver.
    """
    
    def __init__(self, uri: str, user: Optional[str] = None, password: Optional[str] = None):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[Driver] = None

    def connect(self):
        """Establish a connection to the graph database with retry logic."""
        if not self.driver:
            auth = (self.user, self.password) if self.user and self.password else None
            max_retries = 5
            logger.info(f"Attempting to connect to Graph DB at {self.uri}")
            for attempt in range(max_retries):
                try:
                    self.driver = GraphDatabase.driver(self.uri, auth=auth)
                    self.driver.verify_connectivity()
                    logger.success(f"Successfully connected to Graph DB at {self.uri}")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"CRITICAL: Failed to connect to Graph DB at {self.uri} after {max_retries} attempts.")
                        logger.error(f"Error details: {e}")
                        logger.info("Check if Docker containers are running and the port is correct.")
                        raise
                    wait_time = 2 ** attempt
                    logger.warning(f"Connection attempt {attempt + 1} failed for {self.uri}. Retrying in {wait_time}s... Error: {e}")
                    time.sleep(wait_time)

    def disconnect(self):
        """Close the connection to the graph database."""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("Disconnected from Graph DB")

    def initialize_database(self):
        """Initialize the database by loading modules and ensuring basic setup."""
        logger.info("Initializing Graph DB (loading modules)...")
        try:
            self.run_query("CALL mg.load_all();")
            logger.success("Graph DB modules loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Graph DB modules: {e}")
            # We don't raise here as some environments might not support mg.load_all()
            # but we want to know about it.

    def run_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return the results.
        Queries are parameterized to prevent injection.
        """
        if not self.driver:
            self.connect()
        
        start_time = time.time()
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                data = [record.data() for record in result]
                
                duration = time.time() - start_time
                logger.debug(f"Query executed in {duration:.4f}s: {query}")
                return data
        except Exception as e:
            logger.error(f"Error executing Cypher query: {e}\nQuery: {query}\nParams: {parameters}")
            raise

    def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a node with the given label and properties."""
        query = f"CREATE (n:{label} $props) RETURN n"
        result = self.run_query(query, {"props": properties})
        return result[0]["n"] if result else {}

    def get_node(self, node_id: str, label: Optional[str] = None, id_property: str = "id") -> Optional[Dict[str, Any]]:
        """Retrieve a node by its ID and optionally its label."""
        label_str = f":{label}" if label else ""
        query = f"MATCH (n{label_str} {{{id_property}: $node_id}}) RETURN n"
        result = self.run_query(query, {"node_id": node_id})
        return result[0]["n"] if result else None

    def create_edge(self, source_id: str, target_id: str, edge_type: str, 
                    properties: Optional[Dict[str, Any]] = None,
                    source_label: Optional[str] = None, 
                    target_label: Optional[str] = None,
                    id_property: str = "id") -> Dict[str, Any]:
        """
        Create a directed edge between two nodes.
        Uses parameterized source/target IDs and properties.
        """
        s_label = f":{source_label}" if source_label else ""
        t_label = f":{target_label}" if target_label else ""
        
        # Ensure edge_type is a string if it's an Enum
        if hasattr(edge_type, "value"):
            edge_type = edge_type.value

        # Recursively convert Enums in properties to their values
        def sanitize_props(obj):
            if isinstance(obj, dict):
                return {k: sanitize_props(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize_props(i) for i in obj]
            elif hasattr(obj, "value"):
                return obj.value
            return obj

        sanitized_props = sanitize_props(properties or {})
        
        query = (
            f"MATCH (a{s_label} {{{id_property}: $source_id}}), "
            f"(b{t_label} {{{id_property}: $target_id}}) "
            f"CREATE (a)-[r:{edge_type} $props]->(b) "
            f"RETURN r"
        )
        result = self.run_query(query, {
            "source_id": source_id,
            "target_id": target_id,
            "props": sanitized_props
        })
        return result[0]["r"] if result else {}

    def execute_transaction(self, tx_func, *args, **kwargs):
        """Execute a function within a write transaction."""
        if not self.driver:
            self.connect()
            
        with self.driver.session() as session:
            return session.execute_write(tx_func, *args, **kwargs)

