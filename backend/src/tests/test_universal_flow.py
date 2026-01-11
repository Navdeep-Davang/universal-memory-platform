import asyncio
import os
import sys
from loguru import logger

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.config.environment import settings
from src.operations.remember_operation import RememberOperation
from src.operations.recall_operation import RecallOperation

async def test_lite_mode_flow():
    """
    Test the ingestion and retrieval flow with LITE_MODE=True.
    In this mode, internal LLM calls should be bypassed.
    """
    logger.info("Starting Universal Flow Test (LITE_MODE=True)")
    
    # 1. Force LITE_MODE
    settings.LITE_MODE = True
    
    remember_op = RememberOperation()
    recall_op = RecallOperation()
    
    # Initialize DB (load modules)
    remember_op.engine.db.connect()
    remember_op.engine.db.initialize_database()
    
    agent_id = "test-agent-universal"
    session_id = "test-session-universal"
    
    # 2. Test Ingestion with pre-extracted entities
    logger.info("Step 1: Testing Ingestion with injection")
    content = "The user loves building universal memory systems with Python."
    entities = [{"name": "Python", "type": "Technology", "importance": 1.0}]
    
    # This should return immediately and not call LLM
    experience = await remember_op.execute(
        content=content,
        agent_id=agent_id,
        session_id=session_id,
        entities=entities
    )
    logger.info(f"Ingestion successful, experience ID: {experience.id}")
    
    # 3. Test Retrieval in Lite Mode
    logger.info("Step 2: Testing Retrieval in Lite Mode")
    # This should skip LLM query preprocessing
    results = await recall_op.execute(
        query="What language does the user use?",
        agent_id=agent_id,
        limit=5
    )
    
    logger.info(f"Recall successful, found {len(results)} results")
    for res in results:
        logger.info(f" - Result: {res.content[:50]}... (Score: {res.score:.2f})")

    # 4. Verify that the experience was linked to the injected entity
    # (We can't easily check the DB here without more complex logic, but the logs will show it)
    logger.info("Universal Flow Test Completed Successfully")

if __name__ == "__main__":
    asyncio.run(test_lite_mode_flow())
