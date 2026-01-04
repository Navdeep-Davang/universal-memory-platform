# Action Plan: Universal Cognitive Memory Engine

> **Target:** Sub-300ms query performance with >90% accuracy
> **Timeline:** 10 weeks (~100 hours with AI assistance)
> **Architecture:** Plug-and-Play, Open-Source, Adapter-Based

---

## Phase 1: Foundation & Schema Definition (Week 1)

**Time Estimate:** 6.5 hours | **Critical Path:** YES

### GCP Infrastructure & FastAPI Setup

- [X] **Task 1.1:** Create GCP Project & Cloud Services
  - [X] Create GCP project with appropriate naming
  - [X] Enable Cloud Run API
  - [X] Enable Cloud SQL API  
  - [X] Enable Cloud Tasks API
  - [X] Set up GitHub repository with proper `.gitignore`

- [X] **Task 1.2:** Set up Memgraph Cloud Instance
  - [X] Create Memgraph Cloud instance (free tier for MVP)
  - [X] Configure connection credentials
  - [X] Test connection from local environment
  - [X] Document connection string in environment variables

- [X] **Task 1.3:** Create FastAPI Scaffold
  - [X] Initialize FastAPI project with proper structure:
    ```
    universal-memory-engine/
    └── src/
        ├── core/
        ├── strata/
        ├── models/
        ├── reasoning/
        ├── retrieval/
        ├── ranking/
        ├── storage/
        ├── operations/
        ├── conflict_resolution/
        ├── performance/
        ├── api/
        ├── config/
        └── tests/
    ```
  - [X] Create `src/api/rest_api.py` with basic endpoints:
    - `POST /api/memories/add`
    - `GET /api/memories/{id}`
    - `POST /api/query`
    - `GET /health`
  - [X] Implement `src/api/middleware.py` with:
    - CORS middleware
    - Error handling middleware
    - Logging middleware
  - [X] Create `src/config/defaults.py` with default settings
  - [X] Create `src/config/environment.py` for env variable handling
  - [X] Deploy initial version to Cloud Run

### Pydantic Schema Definition

- [X] **Task 1.4:** Create Core Node Models (`src/models/nodes.py`)
  - [X] `Entity` node type:
    - `id`, `name`, `type`, `importance_score`, `created_at`, `updated_at`
  - [X] `Experience` node type:
    - `id`, `agent_id`, `session_id`, `memory_type`, `content`, `embedding`, `created_at`, `updated_at`, `decision_date`, `confidence`, `source`, `reviewed_by`, `metadata`
  - [X] `Context` node type:
    - `id`, `name`, `description`, `importance_score`, `created_at`
  - [X] `Principle` node type:
    - `id`, `content`, `confidence`, `evidence_count`, `created_at`
  - [X] `Goal` node type:
    - `id`, `description`, `status`, `priority`, `created_at`
  - [X] `Constraint` node type:
    - `id`, `description`, `severity`, `created_at`

- [X] **Task 1.5:** Create Edge Models (`src/models/edges.py`)
  - [X] `MENTIONS` relationship (Memory → Entity)
  - [X] `BELONGS_TO` relationship (Memory → Context)
  - [X] `CAUSES` relationship (Experience → Principle)
  - [X] `CONFLICTS_WITH` relationship (Memory → Memory)
  - [X] `SUPPORTS` relationship (Memory → Memory)
  - [X] Relationship status tracking:
    - `status` (pending | resolved | overridden)
    - `resolved_by`, `resolution_date`, `resolution_notes`

- [X] **Task 1.6:** Create Request/Response Models
  - [X] `src/models/memory_request.py`:
    - `MemoryRequest` (query, depth, breadth, reasoning_type, temporal_scope, confidence_threshold)
  - [X] `src/models/memory_result.py`:
    - `MemoryResult` (id, content, score, layer, paths_found, confidence, provenance, supporting_facts, contradictions, related_contexts)
  - [X] Add validation functions and example payloads

### Database Connection

- [X] **Task 1.7:** Create Storage Adapters
  - [X] `src/storage/adapters/graph_db_adapter.py`:
    - Memgraph connection pool
    - `create_node()`, `create_edge()`, `get_node()`, `query()` methods
    - Error handling for connection failures
    - Atomic transaction support
  - [X] `src/storage/backend_registry.py`:
    - Adapter registration system
    - Adapter discovery mechanism

- [X] **Task 1.8:** Create Database Indexes
  - [X] Create index on `memory_id` (primary)
  - [X] Create index on `agent_id` (filtering)
  - [X] Create index on `created_at` (temporal)
  - [X] Prepare for HNSW vector index
  - [X] Prepare for full-text search index

**Deliverable:** Hello-world API responding + database schema ready

---

## Phase 2: Ingestion Pipeline - REMEMBER Operation (Week 2)

**Time Estimate:** 12 hours | **Critical Path:** YES

### Entity Extraction

- [ ] **Task 2.1:** Set up Embedding Adapter
  - [ ] `storage/adapters/embedding_adapter.py`:
    - Integrate sentence-transformers (all-minilm-l6-v2)
    - `embed_text(text)` → 384-dim vector
    - Batch processing (10 at a time)
    - Error handling for GPU OOM

- [ ] **Task 2.2:** Set up LLM Adapter for Entity Extraction
  - [ ] `storage/adapters/llm_adapter.py`:
    - Claude API integration for entity extraction
    - Rate limiting and retry logic
    - Response parsing

- [ ] **Task 2.3:** Implement Experiential Stratum
  - [ ] `strata/experiential_stratum.py`:
    - Extract entities from memory content using LLM
    - Return: name, type, confidence score
    - Check if entity exists (fuzzy match on name)
    - If new: create EntityNode; if exists: increment importance
    - Create MENTIONS edge (Memory → Entity)

### Semantic Encoding & Clustering

- [ ] **Task 2.4:** Set up Cache Adapter
  - [ ] `storage/adapters/cache_adapter.py`:
    - Redis connection management
    - Cache embedding results (key: hash(content))
    - TTL management

- [ ] **Task 2.5:** Implement Contextual Stratum
  - [ ] `strata/contextual_stratum.py`:
    - New memory → embed
    - Vector search against existing contexts (Redis)
    - If similarity > 0.7: merge; else: create new context
    - Create BELONGS_TO edges
    - Update context importance scores

### Abstract Stratum & Ingestion Pipeline

- [ ] **Task 2.6:** Implement Abstract Stratum
  - [ ] `strata/abstract_stratum.py`:
    - Analyze if this is a new causal pattern
    - Link to existing principles or create new
    - Identify counter-examples if applicable
    - Extract reasoning chains if evident

- [ ] **Task 2.7:** Implement Ingest Engine
  - [ ] `core/ingest_engine.py`:
    - Orchestrate ingestion pipeline
    - Parse incoming memory
    - Validate schema (Pydantic models)
    - Check for duplicates (hash-based)
    - Assign unique memory ID

- [ ] **Task 2.8:** Implement Remember Operation
  - [ ] `operations/remember_operation.py`:
    - Accept MemoryRequest
    - Validate + check duplicates
    - Call entity_extraction()
    - Call embed_text()
    - Call context_clustering()
    - Call abstract_stratum processing
    - Create MemoryNode in Memgraph
    - Return {memory_id, status, entities, context_id}
    - Comprehensive error handling

- [ ] **Task 2.9:** Create POST /api/memories/add Endpoint
  - [ ] Wire remember_operation to REST endpoint
  - [ ] Add request validation
  - [ ] Add response formatting
  - [ ] Test end-to-end ingestion

**Deliverable:** POST /api/memories/add working end-to-end

---

## Phase 3: Query Engine - Vector & Keyword Search (Week 3)

**Time Estimate:** 8 hours | **Can Parallelize with Week 2 Day 3+**

### Semantic Vector Search

- [ ] **Task 3.1:** Implement Semantic Retriever
  - [ ] `retrieval/semantic_retriever.py`:
    - Embed query using embedding_adapter
    - Memgraph vector search (HNSW algorithm)
    - Return top N by cosine similarity
    - Apply filters: confidence_threshold, temporal_scope
    - Return [(memory_id, content, score, layer)]

- [ ] **Task 3.2:** Implement Temporal Retriever
  - [ ] `retrieval/temporal_retriever.py`:
    - Filter by temporal window
    - Sort by recency
    - Apply confidence filter
    - Return ranked temporal results

### Keyword Search (BM25)

- [ ] **Task 3.3:** Create Full-Text Search Index
  - [ ] Add FTS index on memory content in Memgraph
  - [ ] Add FTS index on entity names

- [ ] **Task 3.4:** Implement Context Retriever
  - [ ] `retrieval/context_retriever.py`:
    - Full-text search on query
    - Return top N by relevance score
    - Apply filters
    - Combine entity search results

### Result Preparation

- [ ] **Task 3.5:** Implement Result Formatting
  - [ ] Take semantic + keyword results
  - [ ] Format as MemoryResult objects
  - [ ] Add layer, paths_found, confidence, provenance

**Deliverable:** Two independent retrieval paths working (semantic + keyword)

---

## Phase 4: Query Engine - Graph Traversal & Ranking (Week 4)

**Time Estimate:** 13.5 hours | **Critical Path:** YES

### Graph Traversal

- [ ] **Task 4.1:** Implement Graph Retriever
  - [ ] `retrieval/graph_retriever.py`:
    - Extract entities from query
    - Start from entity nodes in graph
    - BFS traversal up to K=3 hops
    - Limit fan-out to 50 per hop (relevance-sorted)
    - Score paths: (similarity × edge_weight) / (1 + 0.2×hops)
    - Filter by relevance threshold
    - Visited set to prevent cycles
    - Timeout after 1 sec

- [ ] **Task 4.2:** Implement Graph Engine
  - [ ] `core/graph_engine.py`:
    - Adaptive K-Hop Limited Traversal (AKHLT) algorithm
    - Path relevance scoring
    - Fan-out limiting
    - Cycle prevention

### Multi-Path Coordination

- [ ] **Task 4.3:** Implement Multi-Path Coordinator
  - [ ] `retrieval/multi_path_coordinator.py`:
    - Launch all 3 retrievals concurrently (semantic, graph, temporal)
    - Wait for all to complete or timeout
    - Merge results from 3 paths
    - Remove duplicates (same memory found via different paths)
    - Track which paths found each result
    - Preserve all path information for transparency

### Ranking System

- [ ] **Task 4.4:** Implement Individual Rankers
  - [ ] `ranking/relevance_ranker.py`: Relevance scoring
  - [ ] `ranking/recency_ranker.py`: Time-decay scoring (1 / (1 + age_days/7))
  - [ ] `ranking/confidence_ranker.py`: Confidence-based scoring
  - [ ] `ranking/reasoning_fit_ranker.py`: Task-type fit scoring

- [ ] **Task 4.5:** Implement Fusion Ranker
  - [ ] `ranking/fusion_ranker.py`:
    - Combine scores from all rankers
    - Apply weights per reasoning type:
      - DESCRIPTIVE: 0.4×recency + 0.4×confidence + 0.2×semantic
      - CAUSAL: 0.4×causal_indicator + 0.3×evidence + 0.3×layer
      - EVALUATIVE: 0.4×has_outcome + 0.3×success_rate + 0.3×feedback
      - PROCEDURAL: 0.4×is_procedure + 0.3×success_rate + 0.3×recency
      - COMPARATIVE: 0.4×alternatives + 0.3×tradeoff_clarity + 0.3×completeness
      - STRATEGIC: 0.4×is_strategic + 0.3×goal_relevance + 0.3×scope
      - CREATIVE: Novelty and divergent thinking weights
    - Final score = weighted sum
    - Sort DESC, limit by breadth

### Recall Engine

- [ ] **Task 4.6:** Implement Recall Engine
  - [ ] `core/recall_engine.py`:
    - Parse recall profile
    - Determine retrieval strategy based on params
    - Build query execution plan
    - Set timeout budgets per retrieval path
    - Orchestrate all retrieval paths
    - Apply fusion ranking
    - Attach provenance

- [ ] **Task 4.7:** Implement Recall Operation
  - [ ] `operations/recall_operation.py`:
    - Execute full recall pipeline
    - Handle breadth expansion
    - Format final results with provenance

- [ ] **Task 4.8:** Create POST /api/query Endpoint
  - [ ] Wire recall_operation to REST endpoint
  - [ ] Test with various query types
  - [ ] Verify <250ms latency target

**Deliverable:** Full 3-path query engine with intelligent ranking

---

## Phase 5: Performance & Caching (Week 5)

**Time Estimate:** 10.5 hours | **Parallel: YES**

### Redis Caching Layer

- [ ] **Task 5.1:** Implement Query Cache
  - [ ] `performance/query_cache.py`:
    - Generate cache key from query params (hash)
    - Check Redis before retrieval
    - If hit: return immediately
    - If miss: run full retrieval, cache result
    - Set TTL: 1 hour for queries, 6 hours for hot nodes
    - Invalidate when memory changes
    - Track hit/miss rate
    - Return result + cache metadata

### Database Optimization

- [ ] **Task 5.2:** Implement Index Manager
  - [ ] `performance/index_manager.py`:
    - Create/manage indexes:
      - memory_id (primary)
      - agent_id (filtering)
      - created_at (temporal)
      - embedding (HNSW vector index)
      - content (full-text search)
    - Analyze query plans for 3 retrieval paths
    - Index rebalancing utilities

- [ ] **Task 5.3:** Implement Query Optimizer
  - [ ] `performance/query_optimizer.py`:
    - Query plan optimization
    - Index selection
    - Early termination strategies

### Performance Monitoring

- [ ] **Task 5.4:** Implement Latency Tracker
  - [ ] `performance/latency_tracker.py`:
    - Measure each path separately (semantic, keyword, graph)
    - Measure dedup + ranking time
    - Log to Cloud Logging with breakdown
    - Track p50, p95, p99 latencies
    - Alert mechanism if p95 > 250ms

- [ ] **Task 5.5:** Implement Profiler
  - [ ] `performance/profiler.py`:
    - Bottleneck identification
    - Memory usage tracking
    - Query performance analysis

- [ ] **Task 5.6:** Set up Cloud Monitoring Dashboard
  - [ ] Create dashboard: p50, p95, p99 latencies
  - [ ] Set up alerts
  - [ ] Cache hit rate visualization

**Deliverable:** Queries now <250ms p95

---

## Phase 6: Conflict Detection (Week 6)

**Time Estimate:** 10.5 hours | **Sequential: YES**

### Conflict Detection System

- [ ] **Task 6.1:** Implement Contradiction Detector
  - [ ] `conflict_resolution/contradiction_detector.py`:
    - When new memory ingested, search for contradictions
    - Vector similarity against existing memories
    - Use LLM to verify actual conflict:
      - Does memory_A genuinely contradict memory_B?
      - Or just different contexts?
    - Cache results (expensive LLM calls)

- [ ] **Task 6.2:** Implement Conflict Analyzer
  - [ ] `conflict_resolution/conflict_analyzer.py`:
    - Determine if contextual or actual conflict
    - Analyze conflict severity
    - Suggest resolution strategies

- [ ] **Task 6.3:** Implement Resolution Engine
  - [ ] `conflict_resolution/resolution_engine.py`:
    - If conflict: create CONFLICTS_WITH edge
    - Track resolution status:
      - status (pending | resolved | overridden)
      - resolved_by (agent_id | human_id | null)
      - resolution_date
      - resolution_notes
    - Apply resolution strategies

### Conflict Operations & API

- [ ] **Task 6.4:** Implement Contradict Operation
  - [ ] `operations/contradict_operation.py`:
    - Conflict detection workflow
    - Resolution tracking

- [ ] **Task 6.5:** Create Conflict API Endpoints
  - [ ] `PUT /api/conflicts/{id}/resolve`:
    - Accept: {status, resolved_by, notes}
    - Return updated metadata
  - [ ] `GET /api/agent/{agent_id}/conflicts`:
    - Return pending conflicts
    - Include memory excerpts, certainty scores
  - [ ] `GET /api/conflicts/{conflict_id}`:
    - Full details + resolution history
  - [ ] Support filtering: agent, time range, status

- [ ] **Task 6.6:** Format Conflict Data for Visualization
  - [ ] Include conflict graph edges
  - [ ] Highlight conflicting memories
  - [ ] Show resolution timeline

**Deliverable:** Conflict detection working - unique feature ready

---

## Phase 7: SDK & Testing (Week 7)

**Time Estimate:** 15 hours | **Parallel: SDK + Tests Simultaneously**

### Python SDK

- [ ] **Task 7.1:** Create Python SDK Package
  - [ ] Create package structure for `agentic-memory`
  - [ ] Client initialization: `client = AgenticMemory(api_key='...', base_url='...')`
  - [ ] Implement methods:
    - `client.remember(content, agent_id, metadata) → memory_id`
    - `client.recall(query, agent_id, depth=2, breadth=50) → results`
    - `client.list_memories(agent_id, limit=100)`
    - `client.get_memory(memory_id)`
    - `client.resolve_conflict(conflict_id, resolution)`
  - [ ] Async versions (async def remember_async(), etc.)
  - [ ] Full docstrings + type hints
  - [ ] Error handling + retries

- [ ] **Task 7.2:** Prepare for PyPI Publishing
  - [ ] Create setup.py/pyproject.toml
  - [ ] Write package README
  - [ ] Configure versioning
  - [ ] Test local installation

### Integration Examples

- [ ] **Task 7.3:** Create Example Scripts
  - [ ] `examples/code_assistant.py`: Coding agent remembering decisions
  - [ ] `examples/research_agent.py`: Research agent tracking sources
  - [ ] `examples/multi_agent_coordinator.py`: 2+ agents sharing memory
  - [ ] `examples/conflict_demo.py`: Detecting/resolving conflicts
  - [ ] `examples/dashboard_demo.py`: Querying and visualizing
  - [ ] Each ~75 lines, runnable with mock data

### Testing Suite

- [ ] **Task 7.4:** Create Unit Tests
  - [ ] `tests/unit/test_entity_extraction.py`: Entity extraction accuracy
  - [ ] `tests/unit/test_embedding.py`: Embedding generation
  - [ ] `tests/unit/test_conflict_detection.py`: Conflict detection
  - [ ] `tests/unit/test_ranking.py`: Ranking algorithm correctness
  - [ ] `tests/unit/test_sdk_client.py`: SDK client methods

- [ ] **Task 7.5:** Create Integration Tests
  - [ ] `tests/integration/test_ingest_pipeline.py`: Full ingest → query pipeline
  - [ ] `tests/integration/test_retrieval.py`: 3-path retrieval accuracy
  - [ ] `tests/integration/test_cache.py`: Cache behavior
  - [ ] `tests/integration/test_conflict_workflow.py`: Conflict workflow end-to-end

- [ ] **Task 7.6:** Create Test Fixtures
  - [ ] `tests/fixtures/sample_memories.json`
  - [ ] `tests/fixtures/sample_agents.json`
  - [ ] `tests/fixtures/sample_queries.json`
  - [ ] Target: 80%+ code coverage

**Deliverable:** SDK ready for customers + test coverage 80%+

---

## Phase 8: Documentation & Hardening (Week 8)

**Time Estimate:** 14 hours | **Parallel: Docs + Load Testing Simultaneously**

### API Documentation

- [ ] **Task 8.1:** Create OpenAPI/Swagger Documentation
  - [ ] Document all endpoints with request/response examples
  - [ ] Define error codes + meanings
  - [ ] Document authentication (API key)
  - [ ] Document rate limits (100 req/sec, 1M/month)
  - [ ] Document latency SLAs (p50 <100ms, p95 <250ms)
  - [ ] Generate interactive Swagger UI at /api/docs

### Load Testing

- [ ] **Task 8.2:** Create Load Test Suite
  - [ ] Set up locust for load testing
  - [ ] Simulate 100 concurrent agents
  - [ ] Each: 10 memories/sec ingestion, 5 queries/sec
  - [ ] Measure: latency, throughput, error rate
  - [ ] Find breaking point
  - [ ] Generate report: max sustainable load

### Security Hardening

- [ ] **Task 8.3:** Implement Security Measures
  - [ ] Input validation (prevent injection)
  - [ ] API key authentication implementation
  - [ ] Rate limiting enforcement
  - [ ] CORS configuration
  - [ ] Comprehensive logging (no secrets in logs)
  - [ ] Error messages (don't leak internals)
  - [ ] Parameterized DB queries
  - [ ] Dependency vulnerability scan (pip audit)

### Monitoring & Alerts

- [ ] **Task 8.4:** Set up Production Monitoring
  - [ ] Metrics: latency (p50/p95/p99), error rate, cache hit rate
  - [ ] Alerts: p95 > 300ms, error rate > 1%, cache < 50%
  - [ ] Deploy Cloud Monitoring dashboard
  - [ ] Configure notification channels

**Deliverable:** Production-hardened, documented, monitored

---

## Phase 9: Dashboard & Polish (Weeks 9-10)

**Time Estimate:** 10 hours | **Parallel: Dashboard + Final Polish**

### React Dashboard

- [ ] **Task 9.1:** Set up Dashboard Project
  - [ ] Initialize Vite + React + TypeScript
  - [ ] Configure Tailwind CSS
  - [ ] Set up project structure

- [ ] **Task 9.2:** Create Dashboard Components
  - [ ] `MemoryGraph`: Visualize graph nodes+edges (D3.js or Cytoscape)
  - [ ] `AgentActivity`: Timeline of ingestions/queries
  - [ ] `Statistics`: Memory counts, breakdown charts
  - [ ] `ConflictViewer`: List conflicts with resolution UI
  - [ ] `QueryBuilder`: Run custom queries

- [ ] **Task 9.3:** Implement Dashboard Features
  - [ ] Call API endpoints to fetch data
  - [ ] Real-time updates (poll every 5 sec)
  - [ ] Mobile responsive design

### Final Polish & Bug Fixes

- [ ] **Task 9.4:** Bug Fixing Sprint
  - [ ] Address edge cases in ranking
  - [ ] Fix timeout handling issues
  - [ ] Resolve cache invalidation edge cases
  - [ ] Improve SDK error messages

### Launch Documentation

- [ ] **Task 9.5:** Create User Documentation
  - [ ] README: What it is, why it matters, quick start
  - [ ] Installation guide: pip install agentic-memory
  - [ ] Usage examples: Copy-paste usage for 5 scenarios
  - [ ] API reference: All endpoints
  - [ ] Troubleshooting: Common issues

- [ ] **Task 9.6:** Deploy Final Version
  - [ ] Deploy dashboard to production
  - [ ] Verify all systems operational
  - [ ] Run final smoke tests

**Deliverable:** Dashboard ready + documentation complete + LAUNCH READY

---

## Success Metrics Checklist

### By End of Week 8 (MVP Ready):
- [ ] Ingest 10,000 memories <200ms latency
- [ ] Query returns 5 results <250ms p95
- [ ] Conflict detection runs on 95%+ of memories
- [ ] Cache hit rate >60%
- [ ] Test coverage >80%
- [ ] Load test passes 100 concurrent agents
- [ ] API fully documented
- [ ] SDK installable + importable
- [ ] Zero security issues in audit

### By End of Week 10 (Launch Ready):
- [ ] Dashboard visualizes memory graph
- [ ] All bugs from feedback fixed
- [ ] Documentation complete + tested
- [ ] Ready to demo to customers

---

## Critical Dependencies

### Hard Blockers (Must Complete Sequentially):
1. Pydantic schema → Everything depends on this
2. Memgraph connection → Ingestion depends on this
3. Embedding pipeline → Clustering depends on this
4. Ingestion endpoint → Queries need data to search
5. Query engine → Ranking needs all 3 paths

### Can Run in Parallel:
- Semantic path vs Keyword path (Phase 3)
- Caching vs Index optimization (Phase 5)
- SDK vs Tests (Phase 7)
- API docs vs Load testing (Phase 8)
- Dashboard vs Final polish (Phase 9)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Memgraph Cypher queries are slow | Phase 4 debug time included. Fallback to simpler graph walks |
| Embedding model doesn't capture meaning well | sentence-transformers is proven. Fallback: fine-tune on domain data |
| Conflict detection LLM calls expensive | Cache aggressively. Only run on high-confidence contradictions |
| One engineer gets blocked on infrastructure | All infrastructure in Phase 1. Once done, pure coding |
| Debugging harder than expected | 2.5 week MVP core. Can launch with ingestion + simple search |

---

*Last Updated: January 2025*
*Architecture Reference: [universal_memory_technical_spec.md](file:///e:/Programs/App/universal-memory-platform/doc/Architecture/universal_memory_technical_spec.md)*
*Roadmap Reference: [dev_roadmap_markdown.md](file:///e:/Programs/App/universal-memory-platform/doc/Architecture/dev_roadmap_markdown.md)*
