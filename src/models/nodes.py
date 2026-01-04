from datetime import datetime
from typing import List, Dict, Optional, Annotated
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class GoalStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class BaseNode(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("updated_at", mode="before")
    @classmethod
    def set_updated_at(cls, v):
        return v or datetime.utcnow()

class Entity(BaseNode):
    name: str = Field(..., description="Name of the entity")
    type: str = Field(..., description="Type of the entity (e.g., Person, Place, Concept)")
    importance_score: Annotated[float, Field(ge=0.0, le=1.0, description="Importance score from 0.0 to 1.0")]

class Experience(BaseNode):
    agent_id: str = Field(..., description="ID of the agent associated with this experience")
    session_id: str = Field(..., description="ID of the session during which this experience occurred")
    memory_type: MemoryType = Field(..., description="Type of memory (episodic, semantic, etc.)")
    content: str = Field(..., description="The textual content of the experience")
    embedding: List[float] = Field(..., description="Vector embedding of the experience content")
    confidence: Annotated[float, Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")]
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")

class Context(BaseModel):
    id: str = Field(..., description="Unique identifier for the context")
    name: str = Field(..., description="Name of the context")
    importance_score: Annotated[float, Field(ge=0.0, le=1.0, description="Importance score from 0.0 to 1.0")]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Principle(BaseNode):
    content: str = Field(..., description="The content of the principle")
    confidence: Annotated[float, Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")]
    evidence_count: int = Field(ge=0, description="Number of experiences supporting this principle")

class Goal(BaseNode):
    description: str = Field(..., description="Description of the goal")
    status: GoalStatus = Field(default=GoalStatus.PENDING, description="Current status of the goal")
    priority: int = Field(..., description="Priority level of the goal")

class Constraint(BaseNode):
    description: str = Field(..., description="Description of the constraint")
    severity: Severity = Field(default=Severity.MEDIUM, description="Severity level of the constraint")

