import httpx
from typing import Dict, Any, List, Optional
import asyncio

class AgenticMemory:
    """
    Client for interacting with the Universal Memory Engine.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {}
        if self.api_key:
            self._headers["X-API-Key"] = self.api_key

    async def remember(
        self, 
        content: str, 
        agent_id: str, 
        session_id: str, 
        memory_type: str = "episodic", 
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Stores a new memory.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/memories/add",
                json={
                    "content": content,
                    "agent_id": agent_id,
                    "session_id": session_id,
                    "memory_type": memory_type,
                    "metadata": metadata or {}
                },
                headers=self._headers
            )
            response.raise_for_status()
            return response.json()

    async def recall(
        self, 
        query: str, 
        agent_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieves relevant memories based on a query.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/query",
                json={
                    "query": query,
                    "agent_id": agent_id,
                    "limit": limit
                },
                headers=self._headers
            )
            response.raise_for_status()
            return response.json().get("results", [])

    async def resolve_conflict(
        self, 
        memory_id: str, 
        resolution_strategy: str = "latest"
    ) -> Dict[str, Any]:
        """
        Resolves conflicts for a specific memory.
        """
        async with httpx.AsyncClient() as client:
            # Note: This endpoint might need implementation on the server side
            response = await client.post(
                f"{self.base_url}/api/memories/{memory_id}/resolve",
                json={"strategy": resolution_strategy},
                headers=self._headers
            )
            response.raise_for_status()
            return response.json()

    # Synchronous versions
    
    def remember_sync(self, *args, **kwargs) -> Dict[str, Any]:
        """Synchronous version of remember."""
        return asyncio.run(self.remember(*args, **kwargs))

    def recall_sync(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Synchronous version of recall."""
        return asyncio.run(self.recall(*args, **kwargs))

    def resolve_conflict_sync(self, *args, **kwargs) -> Dict[str, Any]:
        """Synchronous version of resolve_conflict."""
        return asyncio.run(self.resolve_conflict(*args, **kwargs))

