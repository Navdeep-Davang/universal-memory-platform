from typing import List, Dict, Any, Optional
from loguru import logger
from src.models.nodes import Experience
from src.storage.adapters.graph_db_adapter import GraphDBAdapter
from src.storage.adapters.llm_adapter import LLMAdapter
from src.conflict_resolution.contradiction_detector import ContradictionDetector
from src.conflict_resolution.conflict_analyzer import ConflictAnalyzer
from src.conflict_resolution.resolution_engine import ResolutionEngine
from src.config.environment import settings

class ContradictOperation:
    """
    Unified operation for detecting and recording contradictions.
    """
    def __init__(self, db_adapter: Optional[GraphDBAdapter] = None, llm_adapter: Optional[LLMAdapter] = None):
        # Allow dependency injection or initialize defaults
        self.db = db_adapter or GraphDBAdapter(
            uri=f"bolt://{settings.MEMGRAPH_HOST}:{settings.MEMGRAPH_PORT}",
            user=settings.MEMGRAPH_USERNAME,
            password=settings.MEMGRAPH_PASSWORD
        )
        self.llm = llm_adapter or LLMAdapter(provider="openai")
        
        self.detector = ContradictionDetector(self.db, self.llm)
        self.analyzer = ConflictAnalyzer()
        self.engine = ResolutionEngine(self.db)

    async def execute(self, experience: Experience) -> List[Dict[str, Any]]:
        """
        Executes the conflict detection workflow for a new experience.
        Returns a list of created conflict objects.
        """
        logger.info(f"Executing ContradictOperation for experience {experience.id}")
        
        # 1. Find candidates
        candidates = await self.detector.find_candidate_conflicts(experience)
        if not candidates:
            logger.debug(f"No conflict candidates found for {experience.id}")
            return []

        created_conflicts = []

        # 2. Verify each candidate
        for candidate in candidates:
            # candidate is a dict with 'node' and 'similarity'
            node_data = candidate.get("node", {})
            verification = await self.detector.verify_contradiction(experience, node_data)
            
            # 3. Analyze verification
            analysis = self.analyzer.analyze(verification)
            
            # 4. If confirmed contradiction, record it
            if analysis.get("is_contradiction"):
                conflict_edge = self.engine.create_conflict(
                    source_id=experience.id,
                    target_id=node_data.get("id"),
                    analysis=analysis
                )
                created_conflicts.append({
                    "conflict_id": conflict_edge.id,
                    "target_id": node_data.get("id"),
                    "severity": analysis.get("severity"),
                    "reasoning": analysis.get("reasoning")
                })
        
        logger.info(f"ContradictOperation finished. Found {len(created_conflicts)} contradictions.")
        return created_conflicts

