from typing import Dict, Any, Optional, List
from loguru import logger

from src.core.ingest_engine import IngestEngine
from src.models.nodes import MemoryType, Experience
from src.storage.adapters.embedding_adapter import EmbeddingAdapter
from src.storage.adapters.llm_adapter import LLMAdapter
from src.storage.adapters.cache_adapter import CacheAdapter
from src.storage.adapters.graph_db_adapter import GraphDBAdapter
from src.config.environment import settings

class RememberOperation:
    def __init__(self):
        # In a real app, these would likely be managed by a dependency injection system
        # or a singleton registry. For now, we'll initialize them here.
        self.db_adapter = GraphDBAdapter(
            uri=f"bolt://{settings.MEMGRAPH_HOST}:{settings.MEMGRAPH_PORT}",
            user=settings.MEMGRAPH_USERNAME,
            password=settings.MEMGRAPH_PASSWORD
        )
        self.embedding_adapter = EmbeddingAdapter()
        self.llm_adapter = LLMAdapter(provider=settings.LLM_PROVIDER, model=settings.LLM_MODEL)
        self.cache_adapter = CacheAdapter()
        
        self.engine = IngestEngine(
            db_adapter=self.db_adapter,
            embedding_adapter=self.embedding_adapter,
            llm_adapter=self.llm_adapter,
            cache_adapter=self.cache_adapter
        )

    async def execute(
        self, 
        content: str, 
        agent_id: str, 
        session_id: str, 
        memory_type: str = "episodic",
        metadata: Optional[Dict[str, Any]] = None,
        entities: Optional[List[Dict[str, Any]]] = None,
        principles: Optional[List[Dict[str, Any]]] = None,
        background_tasks: Optional[Any] = None
    ) -> Experience:
        """
        Execute the 'Remember' operation.
        """
        logger.info(f"Executing RememberOperation for content: {content[:50]}...")
        
        # Convert string memory_type to Enum
        try:
            m_type = MemoryType(memory_type.lower())
        except ValueError:
            logger.warning(f"Invalid memory type: {memory_type}, defaulting to EPISODIC")
            m_type = MemoryType.EPISODIC

        # 1. Immediate Ingestion
        experience = await self.engine.ingest(
            content=content,
            agent_id=agent_id,
            session_id=session_id,
            memory_type=m_type,
            metadata=metadata,
            entities=entities,
            principles=principles
        )
        
        # 2. Deferred Enrichment
        if background_tasks:
            background_tasks.add_task(
                self.engine.enrich, 
                experience, 
                entities=entities, 
                principles=principles
            )
        else:
            # Fallback to inline if no background tasks provided
            await self.engine.enrich(experience, entities=entities, principles=principles)
        
        return experience

