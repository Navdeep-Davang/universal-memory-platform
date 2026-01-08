import math
from datetime import datetime, timezone
from typing import List, Optional
from src.models.memory_result import MemoryResult

class RecencyRanker:
    """
    Ranks memories based on their recency using an exponential decay function.
    """
    
    def __init__(self, decay_rate: float = 0.01):
        """
        Initializes the RecencyRanker.
        
        Args:
            decay_rate: The rate at which the score decays over time (hours).
                       Higher values mean faster decay.
        """
        self.decay_rate = decay_rate

    def score(self, memories: List[MemoryResult], reference_time: Optional[datetime] = None) -> List[float]:
        """
        Calculates recency scores for a list of memories.
        
        Formula: score = exp(-decay_rate * hours_since_creation)
        
        Args:
            memories: A list of MemoryResult objects.
            reference_time: The time to calculate recency against. Defaults to now.
            
        Returns:
            A list of float scores between 0 and 1.
        """
        if not reference_time:
            reference_time = datetime.now(timezone.utc)
            
        scores = []
        for memory in memories:
            if not memory.created_at:
                # If no timestamp, assign a neutral or low score
                scores.append(0.5)
                continue
            
            # Ensure created_at has timezone info if reference_time has it
            created_at = memory.created_at
            if created_at.tzinfo is None and reference_time.tzinfo is not None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            
            time_diff = reference_time - created_at
            hours_diff = time_diff.total_seconds() / 3600.0
            
            # Avoid negative time diffs if any
            hours_diff = max(0, hours_diff)
            
            score = math.exp(-self.decay_rate * hours_diff)
            scores.append(score)
            
        return scores

