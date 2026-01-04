from enum import Enum
from typing import Dict, Optional
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

class BackendType(str, Enum):
    MEMGRAPH = "MEMGRAPH"
    NEO4J = "NEO4J"

class BackendRegistry:
    """
    Registry pattern for switching between different graph database backends.
    """
    
    _instances: Dict[BackendType, GraphDBAdapter] = {}

    @classmethod
    def register(cls, backend_type: BackendType, adapter: GraphDBAdapter):
        """Register a specific adapter instance for a backend type."""
        cls._instances[backend_type] = adapter

    @classmethod
    def get_instance(cls, backend_type: BackendType) -> GraphDBAdapter:
        """Retrieve the adapter instance for a backend type."""
        if backend_type not in cls._instances:
            raise ValueError(f"Backend type '{backend_type}' has not been registered in the registry.")
        return cls._instances[backend_type]

    @classmethod
    def list_registered_backends(cls) -> list[BackendType]:
        """Return a list of all registered backend types."""
        return list(cls._instances.keys())

