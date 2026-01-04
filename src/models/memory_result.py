from typing import List, Annotated
from pydantic import BaseModel, Field

class MemoryResult(BaseModel):
    id: str = Field(..., description="Unique identifier of the retrieved memory")
    content: str = Field(..., description="The content of the memory")
    score: Annotated[float, Field(ge=0.0, le=1.0)] = Field(..., description="Relevance score of the memory")
    layer: str = Field(..., description="The memory layer the result was found in (e.g., 'episodic', 'semantic')")
    paths_found: List[str] = Field(default_factory=list, description="List of traversal paths that led to this memory")
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = Field(..., description="Confidence score of the memory")
    provenance: str = Field(..., description="The origin or source of this memory (e.g., session ID, file name)")

