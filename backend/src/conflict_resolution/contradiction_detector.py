from typing import List, Dict, Any, Optional
from loguru import logger
from src.models.nodes import Experience
from src.storage.adapters.graph_db_adapter import GraphDBAdapter
from src.storage.adapters.llm_adapter import LLMAdapter

class ContradictionDetector:
    """
    Detects potential contradictions between a new experience and existing memories.
    """
    def __init__(self, db_adapter: GraphDBAdapter, llm_adapter: LLMAdapter):
        self.db = db_adapter
        self.llm = llm_adapter

    async def find_candidate_conflicts(self, experience: Experience, limit: int = 5, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Find candidates for contradictions using vector search.
        """
        if not experience.embedding:
            logger.warning(f"Experience {experience.id} has no embedding. Cannot search for conflicts.")
            return []

        logger.info(f"Searching for conflict candidates for experience {experience.id}")
        
        # Use Memgraph vector search to find similar experiences
        # Using the correct Memgraph v3.7 procedure
        query = """
        CALL vector_search.search('idx_Experience_embedding', $limit, $embedding) YIELD node, similarity
        WITH node, similarity
        WHERE node.id <> $experience_id AND similarity >= $threshold
        RETURN node, similarity
        """
        params = {
            "embedding": experience.embedding,
            "limit": limit,
            "threshold": threshold,
            "experience_id": experience.id
        }
        
        try:
            results = self.db.run_query(query, params)
            return results
        except Exception as e:
            logger.error(f"Error searching for conflict candidates: {e}")
            return []

    async def verify_contradiction(self, new_experience: Experience, existing_experience_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to verify if two experiences actually contradict each other.
        """
        existing_content = existing_experience_data.get("content", "")
        existing_id = existing_experience_data.get("id", "unknown")
        
        logger.info(f"Verifying potential contradiction between {new_experience.id} and {existing_id}")

        system_prompt = (
            "You are a cognitive contradiction detector. Your task is to determine if two memory fragments "
            "genuinely contradict each other or if they are just describing different contexts, perspectives, or times. "
            "\n\n"
            "Respond ONLY with a JSON object containing:\n"
            "- 'is_contradiction': boolean\n"
            "- 'reasoning': string explaining why it is or isn't a contradiction\n"
            "- 'severity': 'low', 'medium', 'high', or 'critical' (only if is_contradiction is true)\n"
            "- 'resolution_suggestion': string suggesting how to resolve (e.g., 'override with new', 'keep both with context', 'ask user')"
        )

        prompt = (
            f"New Memory: {new_experience.content}\n\n"
            f"Existing Memory: {existing_content}\n\n"
            "Analyze these two fragments. Do they make contradictory claims about the same entity, event, or principle?"
        )

        try:
            result = await self.llm.structured_completion(prompt, system_prompt)
            return result
        except Exception as e:
            logger.error(f"Error verifying contradiction with LLM: {e}")
            return {"is_contradiction": False, "reasoning": f"Error during verification: {str(e)}"}

