from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.middleware import LoggingMiddleware, error_handler_middleware
from src.config.environment import settings
from pydantic import BaseModel
from typing import Dict, Any, List
from src.operations.remember_operation import RememberOperation

app = FastAPI(title="Universal Cognitive Memory Engine")

# Initialize operations
remember_op = RememberOperation()

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

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await error_handler_middleware(request, exc)

class MemoryAddRequest(BaseModel):
    content: str
    agent_id: str
    session_id: str
    memory_type: str = "episodic"
    metadata: Dict[str, Any] = {}

class QueryRequest(BaseModel):
    query: str
    limit: int = 10

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/memories/add")
async def add_memory(request: MemoryAddRequest):
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

@app.get("/api/memories/{memory_id}")
async def get_memory(memory_id: str):
    # Shell implementation
    return {"id": memory_id, "content": "placeholder content"}

@app.post("/api/query")
async def query_memories(request: QueryRequest):
    # Shell implementation
    return {"results": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

