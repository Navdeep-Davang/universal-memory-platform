import asyncio
from agentic_memory import AgenticMemory

async def research_agent_demo():
    client = AgenticMemory(base_url="http://localhost:8000", api_key="dev-key-123")
    
    print("--- Research Agent Memory Demo ---")
    
    # Simulating a research agent gathering info
    findings = [
        "Quantum computing uses qubits instead of bits.",
        "Superposition allows qubits to be in multiple states simultaneously.",
        "Entanglement links qubits across distances.",
        "Quantum decoherence is a major challenge for hardware stability."
    ]
    
    print("Ingesting research findings...")
    for finding in findings:
        await client.remember(
            content=finding,
            agent_id="researcher-01",
            session_id="quantum-study-2026",
            memory_type="semantic"
        )
    
    # Query for specific concept
    print("\nQuerying: How do qubits work?")
    memories = await client.recall(
        query="mechanics of qubits and their states",
        agent_id="researcher-01",
        limit=2
    )
    
    print("Top Research Results:")
    for mem in memories:
        print(f"- {mem['content']}")

if __name__ == "__main__":
    asyncio.run(research_agent_demo())

