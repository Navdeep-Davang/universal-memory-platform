from typing import List, Optional, Dict
from src.models.memory_result import MemoryResult
from src.models.memory_request import ReasoningType
from src.ranking.relevance_ranker import RelevanceRanker
from src.ranking.recency_ranker import RecencyRanker
from src.ranking.confidence_ranker import ConfidenceRanker

class FusionRanker:
    """
    Combines multiple ranking signals to produce a final score for each memory.
    Implements weighted sum fusion with reasoning-type specific weighting profiles.
    """
    
    def __init__(self):
        self.relevance_ranker = RelevanceRanker()
        self.recency_ranker = RecencyRanker()
        self.confidence_ranker = ConfidenceRanker()
        
        # Default weighting profiles for different reasoning types
        self.profiles = {
            ReasoningType.FAST: {
                "relevance": 0.8,
                "recency": 0.1,
                "confidence": 0.1,
                "path_boost": 0.05
            },
            ReasoningType.DEEP: {
                "relevance": 0.4,
                "recency": 0.2,
                "confidence": 0.4,
                "path_boost": 0.1
            },
            ReasoningType.TEMPORAL: {
                "relevance": 0.1,
                "recency": 0.8,
                "confidence": 0.1,
                "path_boost": 0.05
            },
            ReasoningType.CAUSAL: {
                "relevance": 0.4,
                "recency": 0.1,
                "confidence": 0.5,
                "path_boost": 0.15
            },
            ReasoningType.DESCRIPTIVE: {
                "relevance": 0.6,
                "recency": 0.3,
                "confidence": 0.1,
                "path_boost": 0.05
            }
        }

    def _apply_rrf_logic(self, memories: List[MemoryResult], k: int = 60) -> Dict[str, float]:
        """
        Applies Reciprocal Rank Fusion logic to boost memories found through multiple paths.
        Since we don't have the original ranks per path, we treat being found in a path
        as a 'vote' with a default rank of 1.
        
        Args:
            memories: List of unique MemoryResult objects.
            k: RRF constant.
            
        Returns:
            Dictionary mapping memory ID to its RRF boost score.
        """
        boosts = {}
        for memory in memories:
            # If found in multiple paths, boost the score
            # RRF Score = sum(1 / (k + rank))
            # Here we assume rank 1 for each path found
            num_paths = len(memory.paths_found) if memory.paths_found else 1
            boost = sum(1.0 / (k + 1) for _ in range(num_paths))
            boosts[memory.id] = boost
            
        # Normalize boosts to [0, 1] range if needed, or just return as is
        # For simplicity, we'll return the raw boost
        return boosts

    def rank(
        self, 
        memories: List[MemoryResult], 
        query: Optional[str] = None,
        reasoning_type: ReasoningType = ReasoningType.FAST,
        weights: Optional[Dict[str, float]] = None
    ) -> List[MemoryResult]:
        """
        Ranks the merged results using a weighted combination of relevance, recency, 
        confidence, and path-based boosting (RRF-inspired).
        
        Args:
            memories: List of MemoryResult objects from all paths.
            query: The original text query (optional, for future query-specific logic).
            reasoning_type: The type of reasoning to apply for weighting.
            weights: Optional manual weighting overrides.
            
        Returns:
            Sorted list of MemoryResult objects with updated scores.
        """
        if not memories:
            return []
            
        # Use provided weights or fallback to the profile for the reasoning type
        profile = weights if weights else self.profiles.get(reasoning_type, self.profiles[ReasoningType.FAST])
        
        # Calculate individual scores
        relevance_scores = self.relevance_ranker.score(memories)
        recency_scores = self.recency_ranker.score(memories)
        confidence_scores = self.confidence_ranker.score(memories)
        rrf_boosts = self._apply_rrf_logic(memories)
        
        scored_memories = []
        for i, memory in enumerate(memories):
            # Extract weights
            w_rel = profile.get("relevance", 0.0)
            w_rec = profile.get("recency", 0.0)
            w_conf = profile.get("confidence", 0.0)
            w_path = profile.get("path_boost", 0.0)
            
            # Weighted combination
            fused_score = (
                w_rel * relevance_scores[i] +
                w_rec * recency_scores[i] +
                w_conf * confidence_scores[i] +
                w_path * rrf_boosts.get(memory.id, 0.0)
            )
            
            # Normalize fused score to [0, 1]
            # Since individual scores are [0, 1] and boosts are small, 
            # we just clamp to ensure pydantic validation passes
            fused_score = max(0.0, min(1.0, fused_score))
            
            # Update memory score (using model_copy to maintain immutability pattern)
            new_memory = memory.model_copy(update={"score": fused_score})
            scored_memories.append(new_memory)
            
        # Sort by score descending
        scored_memories.sort(key=lambda x: x.score, reverse=True)
        
        return scored_memories
