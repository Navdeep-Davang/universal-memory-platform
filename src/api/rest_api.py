from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.middleware import LoggingMiddleware, ApiKeyMiddleware, RateLimitMiddleware, error_handler_middleware
from src.config.environment import settings
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from src.operations.remember_operation import RememberOperation
from src.operations.recall_operation import RecallOperation
from src.operations.contradict_operation import ContradictOperation
from src.conflict_resolution.resolution_engine import ResolutionEngine
from src.models.edges import RelationshipStatus

app = FastAPI(title="Universal Cognitive Memory Engine")

# Initialize operations
remember_op = RememberOperation()
recall_op = RecallOperation()
contradict_op = ContradictOperation()
resolution_engine = ResolutionEngine(remember_op.db_adapter)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
app.add_middleware(LoggingMiddleware)

# API Key Middleware
app.add_middleware(ApiKeyMiddleware)

# Rate Limiting Middleware
app.add_middleware(
    RateLimitMiddleware, 
    redis_url=settings.REDIS_URL, 
    limit=settings.RATE_LIMIT_PER_MINUTE
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await error_handler_middleware(request, exc)

class MemoryAddRequest(BaseModel):
    content: str = Field(..., description="The text content to remember", json_schema_extra={"example": "The user prefers dark mode."})
    agent_id: str = Field(..., description="Unique identifier for the agent", json_schema_extra={"example": "agent-001"})
    session_id: str = Field(..., description="Unique identifier for the conversation session", json_schema_extra={"example": "session-123"})
    memory_type: str = Field("episodic", description="Type of memory (episodic, semantic, etc.)", json_schema_extra={"example": "episodic"})
    metadata: Dict[str, Any] = Field(default={}, description="Additional structured metadata", json_schema_extra={"example": {"category": "preference"}})

class QueryRequest(BaseModel):
    query: str = Field(..., description="The natural language query to search for", json_schema_extra={"example": "What does the user like?"})
    agent_id: str = Field(..., description="The agent whose memories to search", json_schema_extra={"example": "agent-001"})
    limit: int = Field(10, description="Maximum number of results to return", json_schema_extra={"example": 10})

class ConflictResolveRequest(BaseModel):
    status: str = Field(..., description="The resolution status (e.g., active, superseded)", json_schema_extra={"example": "superseded"})
    resolved_by: str = Field(..., description="Identity of the resolver (agent/user)", json_schema_extra={"example": "user-01"})
    notes: Optional[str] = Field(None, description="Optional notes about the resolution", json_schema_extra={"example": "Updated preference"})

@app.get("/health", tags=["Infrastructure"])
async def health_check():
    """
    Health check endpoint to verify service availability.
    """
    return {"status": "ok"}

@app.post("/api/memories/add", tags=["Memories"], summary="Add a new memory")
async def add_memory(request: MemoryAddRequest):
    """
    Stores a new memory experience in the engine.
    The engine will process the content, extract features, and store it across relevant strata.
    """
    try:
        experience = await remember_op.execute(
            content=request.content,
            agent_id=request.agent_id,
            session_id=request.session_id,
            memory_type=request.memory_type,
            metadata=request.metadata
        )
        return {
            "status": "added", 
            "id": experience.id,
            "agent_id": experience.agent_id,
            "memory_type": experience.memory_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memories/{memory_id}", tags=["Memories"], summary="Get a memory by ID")
async def get_memory(memory_id: str):
    """
    Retrieves a specific memory by its unique identifier.
    """
    # Shell implementation
    return {"id": memory_id, "content": "placeholder content"}

@app.post("/api/query", tags=["Retrieval"], summary="Query memories")
async def query_memories(request: QueryRequest):
    """
    Performs a cognitive recall operation based on the provided query.
    Uses semantic, temporal, and contextual relevance to find the best matches.
    """
    try:
        results = await recall_op.execute(
            query=request.query,
            agent_id=request.agent_id,
            limit=request.limit
        )
        return {"results": [res.model_dump() for res in results]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conflicts", tags=["Conflict Resolution"], summary="Get pending conflicts")
async def get_conflicts(agent_id: Optional[str] = None):
    """
    Retrieves all pending memory conflicts that require resolution.
    Optionally filters by agent ID.
    """
    try:
        conflicts = resolution_engine.get_pending_conflicts(agent_id)
        return {"conflicts": conflicts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/conflicts/{conflict_id}/resolve", tags=["Conflict Resolution"], summary="Resolve a conflict")
async def resolve_conflict(conflict_id: str, request: ConflictResolveRequest):
    """
    Resolves a specific memory conflict by updating its status.
    """
    try:
        try:
            status = RelationshipStatus(request.status.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {request.status}. Must be one of: {[s.value for s in RelationshipStatus]}")

        success = resolution_engine.resolve_conflict(
            conflict_id=conflict_id,
            status=status,
            resolved_by=request.resolved_by,
            notes=request.notes
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Conflict not found or could not be updated")
            
        return {"status": "resolved", "conflict_id": conflict_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

