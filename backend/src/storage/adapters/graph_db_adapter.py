from typing import Any, Dict, List, Optional, Union
from neo4j import GraphDatabase, Driver, Session
import logging
import time

logger = logging.getLogger(__name__)

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
            for attempt in range(max_retries):
                try:
                    self.driver = GraphDatabase.driver(self.uri, auth=auth)
                    self.driver.verify_connectivity()
                    logger.info(f"Connected to Graph DB at {self.uri}")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to connect to Graph DB after {max_retries} attempts: {e}")
                        raise
                    wait_time = 2 ** attempt
                    logger.warning(f"Connection attempt {attempt + 1} failed. Retrying in {wait_time}s... Error: {e}")
                    time.sleep(wait_time)

    def disconnect(self):
        """Close the connection to the graph database."""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("Disconnected from Graph DB")

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
        
        query = (
            f"MATCH (a{s_label} {{{id_property}: $source_id}}), "
            f"(b{t_label} {{{id_property}: $target_id}}) "
            f"CREATE (a)-[r:{edge_type} $props]->(b) "
            f"RETURN r"
        )
        result = self.run_query(query, {
            "source_id": source_id,
            "target_id": target_id,
            "props": properties or {}
        })
        return result[0]["r"] if result else {}

    def execute_transaction(self, tx_func, *args, **kwargs):
        """Execute a function within a write transaction."""
        if not self.driver:
            self.connect()
            
        with self.driver.session() as session:
            return session.execute_write(tx_func, *args, **kwargs)

