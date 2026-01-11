import asyncio
from typing import Dict, Any, List, Optional
from loguru import logger
from src.operations.recall_operation import RecallOperation
from src.operations.remember_operation import RememberOperation
from src.storage.adapters.llm_adapter import LLMAdapter

class MemoryRouter:
    """
    The Memory Router acts as an intelligent proxy between an AI Agent and its LLM.
    It automatically handles memory retrieval before the LLM call and 
    memory ingestion after the LLM call.
    """
    
    def __init__(self, internal_llm: bool = False):
        self.recall_op = RecallOperation()
        self.remember_op = RememberOperation()
        # External LLM adapter if we want the router to handle the call
        self.llm_adapter = LLMAdapter() if internal_llm else None

    async def chat_with_memory(
        self,
        query: str,
        agent_id: str,
        session_id: str,
        external_llm_callback: Optional[Any] = None,
        stream: bool = False
    ) -> str:
        """
        A 'Universal' wrapper for LLM calls with memory.
        1. Contextualize: Fetch relevant memories.
        2. Execute: Call the LLM (client's or internal).
        3. Persist: Save the interaction to memory (background).
        """
        logger.info(f"Router: Processing query with memory for agent {agent_id}")

        # 1. RETRIEVE MEMORIES
        memories = await self.recall_op.execute(query=query, agent_id=agent_id, limit=5)
        context_str = "\n".join([f"- {m.content}" for m in memories])
        
        enriched_prompt = f"""
Relevant Background Memories:
{context_str}

User Query: {query}
"""

        # 2. CALL LLM (Client brings their own or use internal)
        if external_llm_callback:
            # Client's own LLM logic
            response = await external_llm_callback(enriched_prompt)
        elif self.llm_adapter:
            # Internal LLM logic
            response = await self.llm_adapter.acomplete(enriched_prompt)
        else:
            raise ValueError("No LLM provider available in Router.")

        # 3. BACKGROUND INGESTION (Plug and Play)
        # We don't wait for this, making the response fast
        asyncio.create_task(
            self.remember_op.execute(
                content=f"User: {query}\nAssistant: {response}",
                agent_id=agent_id,
                session_id=session_id,
                memory_type="episodic"
            )
        )

        return response

    def generate_system_prompt_with_memory(self, memories: List[Any]) -> str:
        """Helper to generate a system prompt chunk containing memories."""
        if not memories:
            return ""
        
        context = "\n".join([f"- {m.content}" for m in memories])
        return f"\nRELEVANT MEMORIES FOR CONTEXT:\n{context}\n"
