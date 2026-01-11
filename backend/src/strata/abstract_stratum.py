from loguru import logger
import json
import re
import hashlib
from typing import List, Optional, Any
from src.models.nodes import Experience, Principle
from src.models.edges import Edge, RelationshipType
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

class AbstractStratum:
    """
    Handles the abstract layer of memory ingestion.
    Extracts high-level principles and causal relationships.
    """

    def __init__(self, db_adapter: GraphDBAdapter, llm_adapter: Optional[Any] = None):
        self.db = db_adapter
        self.llm = llm_adapter

    async def process(self, experience: Experience, provided_principles: Optional[List[dict]] = None) -> List[Principle]:
        """
        Processes an experience for abstract reasoning:
        1. Derives principles or patterns from the experience using LLM (or uses provided ones).
        2. Links principles to the experience.
        3. Detects causal links between this and other experiences/principles.
        """
        logger.info(f"Processing experience {experience.id} in Abstract Stratum")
        
        # 1. Use provided principles or derive them using LLM
        if provided_principles:
            logger.debug(f"Using {len(provided_principles)} provided principles for experience {experience.id}")
            derived_principles = provided_principles
        else:
            derived_principles = await self._derive_principles(experience.content)
        
        processed_principles = []
        for principle_data in derived_principles:
            content = principle_data.get("content")
            if not content:
                continue
                
            # Use hash of content as a stable ID for principles
            principle_id = f"princ_{hashlib.md5(content.encode()).hexdigest()[:12]}"
            existing_node = self.db.get_node(principle_id, label="Principle")
            
            if existing_node:
                principle = Principle(**existing_node)
                principle.evidence_count += 1
                # Update existing principle node
                self.db.run_query(
                    "MATCH (p:Principle {id: $id}) SET p.evidence_count = $count",
                    {"id": principle.id, "count": principle.evidence_count}
                )
            else:
                principle = Principle(
                    id=principle_id,
                    content=content,
                    confidence=principle_data.get("confidence", 0.7),
                    evidence_count=1
                )
                self.db.create_node("Principle", principle.model_dump())
            
            # 2. Link Principle to Experience
            edge = Edge(
                id=f"{experience.id}_SUPPORTS_{principle.id}",
                source_id=experience.id,
                target_id=principle.id,
                rel_type=RelationshipType.SUPPORTS,
                weight=principle.confidence
            )
            self.db.create_edge(
                source_id=experience.id,
                target_id=principle.id,
                edge_type=RelationshipType.SUPPORTS.value,
                properties=edge.model_dump(),
                source_label="Experience",
                target_label="Principle",
                id_property="id"
            )
            processed_principles.append(principle)
            
        # 3. Causal Detection (Placeholder for future implementation)
        await self._detect_causal_links(experience)
            
        return processed_principles

    async def _derive_principles(self, text: str) -> List[dict]:
        """
        Interacts with LLM to derive high-level principles or reasoning chains.
        """
        if not self.llm:
            logger.warning("LLM adapter not provided. Skipping principle derivation.")
            return []
            
        system_prompt = """You are a high-level reasoning engine for a cognitive memory system.
Your task is to analyze the provided experience and extract abstract principles, lessons, or reasoning patterns.
For each principle, provide:
1. content: A concise statement of the principle or reasoning chain.
2. confidence: A score between 0.0 and 1.0 indicating how strongly this principle is supported by the text.

Return ONLY a JSON array of objects. Example:
[{"content": "Using graph databases improves relational data retrieval efficiency.", "confidence": 0.9}]"""

        prompt = f"Derive abstract principles from the following experience:\n\n{text}"

        try:
            response_text = await self.llm.acomplete(prompt, system_prompt=system_prompt)
            return self._parse_json_response(response_text)
        except Exception as e:
            logger.error(f"Error deriving principles: {e}")
            return []

    def _parse_json_response(self, response_text: str) -> List[dict]:
        """Parses JSON from LLM response, handling potential formatting issues."""
        try:
            match = re.search(r'\[\s*\{.*\}\s*\]', response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Failed to parse JSON response from LLM: {e}. Response was: {response_text}")
            return []

    async def _detect_causal_links(self, experience: Experience):
        """
        Detects if this experience causes or is caused by other nodes.
        Reserved for future iterations.
        """
        pass
