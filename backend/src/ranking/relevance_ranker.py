from typing import List
from src.models.memory_result import MemoryResult

class RelevanceRanker:
    """
    Ranks memories based on their inherent relevance score (e.g., semantic similarity).
    """
    
    def score(self, memories: List[MemoryResult]) -> List[float]:
        """
        Extracts and returns the relevance scores from the memories.
        
        Args:
            memories: A list of MemoryResult objects.
            
        Returns:
            A list of float scores, normalized between 0 and 1.
        """
        # MemoryResult.score is already expected to be between 0 and 1
        return [memory.score for memory in memories]

