import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger

from src.models.nodes import Experience, MemoryType
from src.storage.adapters.embedding_adapter import EmbeddingAdapter
from src.storage.adapters.llm_adapter import LLMAdapter
from src.storage.adapters.cache_adapter import CacheAdapter
from src.storage.adapters.graph_db_adapter import GraphDBAdapter

from src.strata.experiential_stratum import ExperientialStratum
from src.strata.contextual_stratum import ContextualStratum
from src.strata.abstract_stratum import AbstractStratum

class IngestEngine:
    def __init__(
        self, 
        db_adapter: GraphDBAdapter,
        embedding_adapter: EmbeddingAdapter,
        llm_adapter: LLMAdapter,
        cache_adapter: Optional[CacheAdapter] = None
    ):
        self.db = db_adapter
        self.embedding_adapter = embedding_adapter
        self.llm_adapter = llm_adapter
        self.cache_adapter = cache_adapter
        
        # Initialize strata
        self.experiential = ExperientialStratum(self.db, self.llm_adapter)
        self.contextual = ContextualStratum(self.db, self.embedding_adapter)
        self.abstract = AbstractStratum(self.db, self.llm_adapter)

    async def ingest(
        self, 
        content: str, 
        agent_id: str, 
        session_id: str, 
        memory_type: MemoryType = MemoryType.EPISODIC,
        metadata: Dict[str, Any] = None
    ) -> Experience:
        """
        Orchestrate the ingestion flow:
        1. Deduplicate/Cache check
        2. Generate Embedding
        3. Create Experience node
        4. Run Strata (Experiential, Contextual, Abstract)
        5. Return the created Experience
        """
        logger.info(f"Starting ingestion for agent {agent_id}, session {session_id}")
        
        # 1. Cache/Deduplication check
        embedding = None
        if self.cache_adapter:
            embedding = self.cache_adapter.get_embedding(content)
            
        # 2. Generate Embedding if not cached
        if not embedding:
            embedding = self.embedding_adapter.embed_text(content)
            if self.cache_adapter:
                self.cache_adapter.set_embedding(content, embedding)
        
        # 3. Create Experience node
        experience = Experience(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            session_id=session_id,
            memory_type=memory_type,
            content=content,
            embedding=embedding,
            confidence=1.0, # Initial confidence for raw experience
            metadata=metadata or {}
        )
        
        # Write Experience to Graph DB
        self.db.create_node("Experience", experience.model_dump())
        logger.debug(f"Created Experience node: {experience.id}")
        
        # 4. Run Strata
        try:
            # Run in sequence for now to ensure consistency, 
            # though some could potentially be parallelized.
            
            # Experiential: Entity extraction
            entities = await self.experiential.process(experience)
            logger.debug(f"Experiential stratum processed: {len(entities)} entities found")
            
            # Contextual: Clustering
            context = await self.contextual.process(experience)
            logger.debug(f"Contextual stratum processed: {context.id if context else 'None'}")
            
            # Abstract: Principle derivation
            principles = await self.abstract.process(experience)
            logger.debug(f"Abstract stratum processed: {len(principles)} principles derived")
            
        except Exception as e:
            logger.error(f"Error during strata processing: {e}")
            # We might want to mark the experience as "partially processed" here
            
        return experience

