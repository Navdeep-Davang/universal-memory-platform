from datetime import datetime
from typing import Optional, Annotated
from enum import Enum
from pydantic import BaseModel, Field

class RelationshipType(str, Enum):
    MENTIONS = "MENTIONS"
    BELONGS_TO = "BELONGS_TO"
    CAUSES = "CAUSES"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    SUPPORTS = "SUPPORTS"

class RelationshipStatus(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    OVERRIDDEN = "overridden"

class Edge(BaseModel):
    id: str = Field(..., description="Unique identifier for the edge")
    source_id: str = Field(..., description="ID of the source node")
    target_id: str = Field(..., description="ID of the target node")
    rel_type: RelationshipType = Field(..., description="Type of relationship")
    status: RelationshipStatus = Field(default=RelationshipStatus.PENDING, description="Current status of the relationship")
    weight: Annotated[float, Field(ge=0.0, le=1.0)] = Field(default=1.0, description="Strength of the relationship")
    resolved_by: Optional[str] = Field(None, description="ID of the agent or process that resolved this relationship")
    resolution_date: Optional[datetime] = Field(None, description="When the relationship was resolved")
    resolution_notes: Optional[str] = Field(None, description="Notes about the resolution")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

