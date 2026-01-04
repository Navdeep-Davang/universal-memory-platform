from typing import Optional, Annotated
from enum import Enum
from pydantic import BaseModel, Field

class ReasoningType(str, Enum):
    FAST = "fast"
    DEEP = "deep"
    TEMPORAL = "temporal"
    CAUSAL = "causal"

class MemoryRequest(BaseModel):
    query: str = Field(..., description="The query string to search for in memory")
    depth: int = Field(default=3, ge=1, le=10, description="The depth of the search in the memory graph")
    breadth: int = Field(default=50, ge=1, le=1000, description="The maximum number of nodes to explore at each level")
    reasoning_type: ReasoningType = Field(default=ReasoningType.FAST, description="The type of reasoning to apply during retrieval")
    temporal_scope: Optional[str] = Field(None, description="Optional temporal constraint (e.g., 'last 24h', '2023')")
    confidence_threshold: Annotated[float, Field(ge=0.0, le=1.0)] = Field(default=0.5, description="Minimum confidence score for retrieved memories")

