import asyncio
import os
import sys

# Add the parent directory to sys.path so we can import agentic_memory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agentic_memory import AgenticMemory

async def universal_headless_demo():
    """
    This demo shows how an AI agent can use the Universal Memory Platform
    in a 'headless' or 'lite' mode. 
    
    The agent performs its own intelligence tasks (entity extraction) and 
    only uses the platform for structured storage and multi-path retrieval.
    """
    API_KEY = os.getenv("MEMORY_API_KEY", "dev-key-123")
    client = AgenticMemory(base_url="http://localhost:8000", api_key=API_KEY)
    
    print("--- Universal 'Headless' Memory Demo ---")
    
    agent_id = "universal-agent-01"
    session_id = "session-headless-999"

    # 1. AGENT-SIDE INTELLIGENCE (Pre-extraction)
    # Imagine the agent has its own LLM logic here
    content = "The user is an expert in Rust programming and lives in Berlin."
    
    print(f"Agent processing content: '{content}'")
    
    # Pre-extracted features (Agent brings its own 'intelligence')
    injected_entities = [
        {"name": "Rust", "type": "Technology", "importance": 1.0},
        {"name": "Berlin", "type": "Location", "importance": 0.8}
    ]
    
    injected_principles = [
        {"content": "User has high technical expertise in systems programming.", "confidence": 0.9}
    ]

    # 2. STORE WITH INJECTED FEATURES
    # The platform will skip its internal LLM extraction for these
    print("Storing memory with pre-extracted entities and principles...")
    await client.remember(
        content=content,
        agent_id=agent_id,
        session_id=session_id,
        entities=injected_entities,
        principles=injected_principles
    )

    # 3. RECALL WITH PRE-EXTRACTED ENTITIES
    # Even during retrieval, the agent can guide the search
    query = "What do we know about the user's technical skills?"
    print(f"\nRecalling for query: '{query}'")
    
    # Guided recall bypasses internal LLM query analysis
    results = await client.recall(
        query=query,
        agent_id=agent_id,
        entities=["Rust"]  # Specifically guiding the graph search path
    )
    
    print("\nRecall Results:")
    for i, res in enumerate(results):
        print(f"[{i+1}] {res['content']} (Score: {res.get('final_score', 'N/A')})")

if __name__ == "__main__":
    asyncio.run(universal_headless_demo())
