import logging
import json
import re
from typing import List, Optional
from src.models.nodes import Experience, Entity
from src.models.edges import Edge, RelationshipType
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

logger = logging.getLogger(__name__)

class ExperientialStratum:
    """
    Handles the experiential layer of memory ingestion.
    Extracts entities from raw experiences and links them.
    """

    def __init__(self, db_adapter: GraphDBAdapter, llm_adapter: Optional[any] = None):
        self.db = db_adapter
        self.llm = llm_adapter

    async def process(self, experience: Experience) -> List[Entity]:
        """
        Processes a raw experience:
        1. Extracts entities from the content.
        2. Checks for existing entities in the graph.
        3. Creates/updates entities and links them to the experience.
        """
        logger.info(f"Processing experience {experience.id} in Experiential Stratum")
        
        # 1. Extract entities using LLM (if available)
        extracted_entities = await self._extract_entities(experience.content)
        
        processed_entities = []
        for entity_data in extracted_entities:
            # 2. Check for existing entity
            name = entity_data.get("name")
            if not name:
                continue
                
            existing_node = self.db.get_node(name, label="Entity", id_property="name")
            
            if existing_node:
                entity = Entity(**existing_node)
                # Update importance: simple average for now
                new_importance = (entity.importance_score + entity_data.get("importance", 0.5)) / 2
                self.db.run_query(
                    "MATCH (e:Entity {name: $name}) SET e.importance_score = $importance",
                    {"name": name, "importance": new_importance}
                )
                entity.importance_score = new_importance
            else:
                # Create new entity
                entity = Entity(
                    id=name, # Using name as ID for simplicity
                    name=name,
                    type=entity_data.get("type", "Unknown"),
                    importance_score=entity_data.get("importance", 0.5)
                )
                self.db.create_node("Entity", entity.model_dump())
            
            # 3. Create MENTIONS relationship
            edge = Edge(
                id=f"{experience.id}_MENTIONS_{entity.id}",
                source_id=experience.id,
                target_id=entity.id,
                rel_type=RelationshipType.MENTIONS,
                weight=1.0
            )
            self.db.create_edge(
                source_id=experience.id, 
                target_id=entity.id, 
                edge_type=RelationshipType.MENTIONS,
                properties=edge.model_dump(),
                source_label="Experience",
                target_label="Entity",
                id_property="id"
            )
            processed_entities.append(entity)
            
        return processed_entities

    async def _extract_entities(self, text: str) -> List[dict]:
        """
        Interacts with LLM to extract entities using a structured prompt.
        """
        if not self.llm:
            logger.warning("LLM adapter not provided. Skipping entity extraction.")
            return []
        
        system_prompt = """You are a highly precise entity extraction engine for a cognitive memory graph.
Your task is to identify key entities (People, Places, Organizations, Concepts, Technologies, etc.) from the provided text.
For each entity, provide:
1. name: The most common or canonical name.
2. type: The category of the entity.
3. importance: A score between 0.0 and 1.0 indicating how central the entity is to the text.

Return ONLY a JSON array of objects. Example:
[{"name": "Neo4j", "type": "Technology", "importance": 0.8}, {"name": "Graph Database", "type": "Concept", "importance": 0.9}]"""

        prompt = f"Extract entities from the following text:\n\n{text}"

        try:
            response_text = await self.llm.acomplete(prompt, system_prompt=system_prompt)
            return self._parse_json_response(response_text)
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []

    def _parse_json_response(self, response_text: str) -> List[dict]:
        """Parses JSON from LLM response, handling potential formatting issues."""
        try:
            # Try to find JSON array in the response
            match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Failed to parse JSON response from LLM: {e}. Response was: {response_text}")
            return []

