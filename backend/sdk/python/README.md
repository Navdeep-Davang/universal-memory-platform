# Agentic Memory Python SDK

A client for interacting with the Universal Memory Engine.

## Installation

```bash
pip install .
```

## Basic Usage

```python
import asyncio
from agentic_memory import AgenticMemory

async def main():
    client = AgenticMemory(base_url="http://localhost:8000", api_key="your-api-key")
    
    # Remember something
    await client.remember(
        content="The user likes coffee",
        agent_id="agent-001",
        session_id="session-123"
    )
    
    # Recall something
    memories = await client.recall(
        query="What does the user like?",
        agent_id="agent-001"
    )
    print(memories)

if __name__ == "__main__":
    asyncio.run(main())
```

