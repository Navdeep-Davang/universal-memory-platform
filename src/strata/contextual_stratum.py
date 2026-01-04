import logging
from typing import List, Optional
from src.models.nodes import Experience, Context
from src.models.edges import Edge, RelationshipType
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

logger = logging.getLogger(__name__)

class ContextualStratum:
    """
    Handles the contextual layer of memory ingestion.
    Clusters experiences into contexts based on semantic similarity.
    """

    def __init__(self, db_adapter: GraphDBAdapter, embedding_adapter: Optional[any] = None):
        self.db = db_adapter
        self.embedding_adapter = embedding_adapter

    async def process(self, experience: Experience) -> Optional[Context]:
        """
        Processes an experience for contextual clustering:
        1. Searches for existing similar experiences or contexts.
        2. Assigns the experience to an existing context or creates a new one.
        3. Creates a BELONGS_TO relationship.
        """
        logger.info(f"Processing experience {experience.id} in Contextual Stratum")
        
        # 1. Find similar context using vector search
        similar_context = await self._find_similar_context(experience.embedding)
        
        if similar_context:
            context = similar_context
        else:
            # Create a new context if no similar one is found
            # In a more advanced version, we would use an LLM to generate a descriptive name
            context = Context(
                id=f"ctx_{experience.id[:8]}",
                name=f"Context for Experience {experience.id[:8]}",
                importance_score=0.5
            )
            self.db.create_node("Context", context.model_dump())
        
        # 2. Create BELONGS_TO relationship
        edge = Edge(
            id=f"{experience.id}_BELONGS_TO_{context.id}",
            source_id=experience.id,
            target_id=context.id,
            rel_type=RelationshipType.BELONGS_TO,
            weight=1.0
        )
        self.db.create_edge(
            source_id=experience.id,
            target_id=context.id,
            edge_type=RelationshipType.BELONGS_TO,
            properties=edge.model_dump(),
            source_label="Experience",
            target_label="Context",
            id_property="id"
        )
        
        return context

    async def _find_similar_context(self, embedding: List[float], threshold: float = 0.8) -> Optional[Context]:
        """
        Finds an existing context that is semantically similar to the experience
        using Memgraph's vector search capabilities.
        """
        if not embedding:
            return None
            
        try:
            # Memgraph vector search query
            # We search for the most similar experience and return its context
            query = """
            CALL vector.search(:Experience, 'embedding', $embedding, 5) YIELD node, similarity
            MATCH (node)-[:BELONGS_TO]->(c:Context)
            RETURN c, similarity
            ORDER BY similarity DESC
            LIMIT 1
            """
            results = self.db.run_query(query, {"embedding": embedding})
            
            if results and results[0]["similarity"] >= threshold:
                context_data = results[0]["c"]
                return Context(**context_data)
                
        except Exception as e:
            logger.error(f"Error during vector search for context: {e}")
            
        return None

