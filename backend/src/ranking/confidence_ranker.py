from typing import List
from src.models.memory_result import MemoryResult

class ConfidenceRanker:
    """
    Ranks memories based on their confidence score.
    """
    
    def score(self, memories: List[MemoryResult]) -> List[float]:
        """
        Extracts and returns the confidence scores from the memories.
        
        Args:
            memories: A list of MemoryResult objects.
            
        Returns:
            A list of float scores between 0 and 1.
        """
        return [memory.confidence for memory in memories]

