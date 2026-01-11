import asyncio
import os
from agentic_memory import AgenticMemory

async def assistant_memory_demo():
    # In a real scenario, you'd get this from environment variables
    API_KEY = os.getenv("MEMORY_API_KEY", "dev-key-123")
    client = AgenticMemory(base_url="http://localhost:8000", api_key=API_KEY)
    
    print("--- Personal Assistant Memory Demo ---")
    
    # 1. Store user preference
    print("Storing preference: User prefers dark mode...")
    await client.remember(
        content="The user prefers dark mode for all applications.",
        agent_id="assistant-01",
        session_id="session-xyz",
        metadata={"category": "preference", "importance": "high"}
    )
    
    # 2. Store another fact
    print("Storing fact: User's favorite color is blue...")
    await client.remember(
        content="The user's favorite color is blue.",
        agent_id="assistant-01",
        session_id="session-xyz"
    )
    
    # 3. Recall information
    print("\nRecalling preferences...")
    results = await client.recall(
        query="What are the user's UI preferences?",
        agent_id="assistant-01"
    )
    
    for i, res in enumerate(results):
        print(f"[{i+1}] {res['content']} (Confidence: {res.get('confidence', 'N/A')})")

if __name__ == "__main__":
    asyncio.run(assistant_memory_demo())

