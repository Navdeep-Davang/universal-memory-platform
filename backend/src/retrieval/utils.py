from typing import Any, Dict, List
from src.models.memory_result import MemoryResult

def format_memory_result(record: Dict[str, Any], score: float = 0.0, layer: str = "unknown") -> MemoryResult:
    """
    Format a raw database record from Memgraph/Neo4j into a MemoryResult object.
    
    Args:
        record: The raw record data from the database (usually from record.data() in Neo4j driver).
        score: The relevance score (semantic similarity or FTS score).
        layer: The memory layer the result was retrieved from.
        
    Returns:
        A MemoryResult pydantic model instance.
    """
    # Neo4j record.data() usually returns {"n": {"id": "...", "content": "...", ...}} 
    # if the query was "MATCH (n) RETURN n"
    node = record.get("n", record)
    
    # Handle cases where the record might be the properties directly
    content = node.get("content", "")
    node_id = node.get("id", "unknown")
    confidence = node.get("confidence", 0.0)
    
    # Provenance often comes from session_id or metadata in Experience nodes
    provenance = node.get("session_id") or node.get("provenance") or "unknown"
    
    # Default layer to memory_type if available in the node
    final_layer = node.get("memory_type", layer)
    
    return MemoryResult(
        id=str(node_id),
        content=content,
        score=float(score),
        layer=str(final_layer),
        paths_found=[], # Can be populated by path-based retrieval later
        confidence=float(confidence),
        provenance=str(provenance)
    )

