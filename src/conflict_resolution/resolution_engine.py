import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger
from src.models.edges import Edge, RelationshipType, RelationshipStatus
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

class ResolutionEngine:
    """
    Manages the lifecycle of CONFLICTS_WITH relationships in the graph.
    """
    def __init__(self, db_adapter: GraphDBAdapter):
        self.db = db_adapter

    def create_conflict(
        self, 
        source_id: str, 
        target_id: str, 
        analysis: Dict[str, Any]
    ) -> Edge:
        """
        Creates a CONFLICTS_WITH edge between two memories.
        """
        logger.info(f"Creating CONFLICTS_WITH edge between {source_id} and {target_id}")
        
        edge_id = f"conf_{uuid.uuid4().hex[:8]}"
        edge = Edge(
            id=edge_id,
            source_id=source_id,
            target_id=target_id,
            rel_type=RelationshipType.CONFLICTS_WITH,
            status=RelationshipStatus.PENDING,
            weight=1.0, # Initial weight for a conflict
            resolution_notes=analysis.get("reasoning", "")
        )
        
        # Use existing create_edge method from adapter
        self.db.create_edge(
            source_id=source_id,
            target_id=target_id,
            edge_type=RelationshipType.CONFLICTS_WITH,
            properties=edge.model_dump(),
            source_label="Experience",
            target_label="Experience"
        )
        
        return edge

    def resolve_conflict(
        self, 
        conflict_id: str, 
        status: RelationshipStatus, 
        resolved_by: str, 
        notes: Optional[str] = None
    ) -> bool:
        """
        Updates the status of a conflict edge.
        """
        logger.info(f"Resolving conflict {conflict_id} with status {status}")
        
        query = """
        MATCH ()-[r:CONFLICTS_WITH {id: $conflict_id}]->()
        SET r.status = $status,
            r.resolved_by = $resolved_by,
            r.resolution_date = $resolution_date,
            r.resolution_notes = $notes,
            r.updated_at = $updated_at
        RETURN r
        """
        now = datetime.utcnow().isoformat()
        params = {
            "conflict_id": conflict_id,
            "status": status.value,
            "resolved_by": resolved_by,
            "resolution_date": now,
            "notes": notes,
            "updated_at": now
        }
        
        try:
            results = self.db.run_query(query, params)
            return len(results) > 0
        except Exception as e:
            logger.error(f"Error resolving conflict: {e}")
            return False

    def get_pending_conflicts(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves all pending conflicts, optionally filtered by agent.
        """
        query = """
        MATCH (a:Experience)-[r:CONFLICTS_WITH {status: 'pending'}]->(b:Experience)
        """
        if agent_id:
            query += " WHERE a.agent_id = $agent_id "
        
        query += " RETURN r, a.content as source_content, b.content as target_content, a.id as source_id, b.id as target_id"
        
        params = {"agent_id": agent_id} if agent_id else {}
        
        try:
            return self.db.run_query(query, params)
        except Exception as e:
            logger.error(f"Error fetching pending conflicts: {e}")
            return []

