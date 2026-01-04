# UNIVERSAL COGNITIVE MEMORY ENGINE
## Technical Specification & Implementation Blueprint
### Sub-300ms Query Performance with Enterprise-Grade Accuracy

**Document Version:** 1.0  
**Status:** Ready for Implementation Review  
**Last Updated:** January 2025  
**Target Performance:** <300ms P95 latency, >90% accuracy vs SuperMemory  
**Architecture:** Plug-and-Play, Open-Source, Adapter-Based

---

## 1. PROJECT STRUCTURE & ORGANIZATION

```
universal-memory-engine/
│
├── core/
│   ├── memory_controller.py          # Orchestration engine
│   ├── graph_engine.py                # Graph operations & traversal
│   ├── recall_engine.py               # Query execution
│   ├── ingest_engine.py               # Memory ingestion pipeline
│   └── reasoning_engine.py            # Reasoning type orchestration
│
├── strata/
│   ├── experiential_stratum.py        # Layer 1: Facts & experiences
│   ├── contextual_stratum.py          # Layer 2: Semantic clusters
│   └── abstract_stratum.py            # Layer 3: Principles & causality
│
├── models/
│   ├── nodes.py                       # Node type definitions (Entity, Experience, Context, Principle, Goal, Constraint)
│   ├── edges.py                       # Edge type definitions & relationships
│   ├── memory_request.py              # Recall profile specification
│   └── memory_result.py               # Result format & provenance
│
├── reasoning/
│   ├── descriptive_reasoner.py        # "What?" reasoning
│   ├── causal_reasoner.py             # "Why?" reasoning
│   ├── evaluative_reasoner.py         # "Is this good?" reasoning
│   ├── procedural_reasoner.py         # "How?" reasoning
│   ├── comparative_reasoner.py        # "Which is better?" reasoning
│   ├── strategic_reasoner.py          # "What should we do?" reasoning
│   └── creative_reasoner.py           # "What if?" reasoning
│
├── retrieval/
│   ├── semantic_retriever.py          # Vector-based retrieval (semantic path)
│   ├── graph_retriever.py             # Graph-based retrieval (relationship path)
│   ├── temporal_retriever.py          # Time-based retrieval (temporal path)
│   ├── context_retriever.py           # Context-aware retrieval
│   └── multi_path_coordinator.py      # Parallel retrieval orchestration
│
├── ranking/
│   ├── relevance_ranker.py            # Relevance scoring
│   ├── recency_ranker.py              # Time-decay scoring
│   ├── confidence_ranker.py           # Confidence-based scoring
│   ├── reasoning_fit_ranker.py        # Task-type fit scoring
│   └── fusion_ranker.py               # Combined score fusion
│
├── storage/
│   ├── adapters/
│   │   ├── vector_db_adapter.py       # Interface for Qdrant, Chroma, etc
│   │   ├── graph_db_adapter.py        # Interface for Memgraph, Neo4j, etc
│   │   ├── cache_adapter.py           # Interface for Redis, DuckDB, etc
│   │   ├── embedding_adapter.py       # Interface for embedding services
│   │   ├── reasoning_adapter.py       # Interface for reasoning engines
│   │   ├── llm_adapter.py             # Interface for LLM communication
│   │   └── persistence_adapter.py     # Interface for storage backends
│   │
│   └── backend_registry.py            # Adapter registration & discovery
│
├── operations/
│   ├── remember_operation.py          # Ingestion pipeline
│   ├── recall_operation.py            # Retrieval pipeline
│   ├── reflect_operation.py           # Principle extraction
│   ├── contradict_operation.py        # Conflict detection & handling
│   └── forget_operation.py            # Archival & removal
│
├── conflict_resolution/
│   ├── contradiction_detector.py      # Identifies conflicting memories
│   ├── conflict_analyzer.py           # Determines if contextual or actual
│   └── resolution_engine.py           # Applies resolution strategy
│
├── performance/
│   ├── query_cache.py                 # Result caching layer
│   ├── index_manager.py               # Index optimization & management
│   ├── query_optimizer.py             # Query plan optimization
│   ├── latency_tracker.py             # Performance monitoring
│   └── profiler.py                    # Bottleneck identification
│
├── api/
│   ├── rest_api.py                    # REST endpoint definitions
│   ├── grpc_api.py                    # gRPC interface
│   └── middleware.py                  # Authentication, rate limiting, logging
│
├── config/
│   ├── defaults.py                    # Default configuration
│   ├── schema.py                      # Configuration validation
│   └── environment.py                 # Environment variable handling
│
└── tests/
    ├── unit/                          # Unit tests per module
    ├── integration/                   # Integration tests
    ├── performance/                   # Latency & accuracy benchmarks
    └── fixtures/                      # Test data & utilities
```

---

## 2. DATA FLOW PIPELINE

### 2.1 INGESTION PIPELINE (REMEMBER Operation)

```
AGENT INPUT (External)
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 1: REQUEST PARSING & VALIDATION           │
├─────────────────────────────────────────────────┤
│ File: ingest_engine.py / remember_operation.py  │
│ Process:                                        │
│  ├─ Parse incoming memory (fact, context, etc) │
│  ├─ Validate schema (Pydantic models)          │
│  ├─ Check for duplicates (hash-based)          │
│  └─ Assign unique memory ID                    │
│ Time: <5ms                                      │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 2: ENTITY EXTRACTION & LINKING            │
├─────────────────────────────────────────────────┤
│ File: strata/experiential_stratum.py           │
│ Process:                                        │
│  ├─ Extract entities (people, concepts, etc)   │
│  ├─ Link to existing entity nodes or create    │
│  ├─ Update entity importance scores            │
│  └─ Create MENTIONS relationships              │
│ Time: <20ms (batch processing)                 │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 3: SEMANTIC ENCODING & EMBEDDING          │
├─────────────────────────────────────────────────┤
│ File: adapters/embedding_adapter.py            │
│ Process:                                        │
│  ├─ Generate embedding vector (parallel)       │
│  ├─ Store embedding metadata                   │
│  └─ Prepare for vector index insertion         │
│ Time: <30ms (on GPU: <5ms)                     │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 4: CONTEXTUAL CLUSTERING                  │
├─────────────────────────────────────────────────┤
│ File: strata/contextual_stratum.py             │
│ Process:                                        │
│  ├─ Find semantically similar existing contexts│
│  ├─ Determine fit: create new or merge into    │
│  │  existing context                           │
│  ├─ Update context relationships               │
│  └─ Maintain context importance scores         │
│ Time: <15ms (semantic similarity search)       │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 5: CAUSAL ANALYSIS & PRINCIPLE EXTRACTION │
├─────────────────────────────────────────────────┤
│ File: reasoning_engine.py / abstract_stratum.py│
│ Process:                                        │
│  ├─ Analyze if this is a new causal pattern    │
│  ├─ Link to existing principles or create new  │
│  ├─ Identify counter-examples if applicable    │
│  └─ Extract reasoning chains if evident        │
│ Time: <50ms (LLM-based analysis)               │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 6: CONFLICT DETECTION                     │
├─────────────────────────────────────────────────┤
│ File: conflict_resolution/contradiction_*.py   │
│ Process:                                        │
│  ├─ Check for contradictory memories           │
│  ├─ If found, determine if contextual or real  │
│  ├─ Flag contradictions for agent awareness    │
│  └─ Update confidence scores accordingly       │
│ Time: <10ms (vector similarity comparison)     │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 7: GRAPH COMMIT (ATOMIC TRANSACTION)      │
├─────────────────────────────────────────────────┤
│ File: adapters/graph_db_adapter.py             │
│ Process:                                        │
│  ├─ Create nodes in graph (Experience node)    │
│  ├─ Create edges to entities, contexts, etc    │
│  ├─ Commit as atomic transaction               │
│  └─ Confirm success or rollback                │
│ Time: <10ms (graph write)                      │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 8: INDEX UPDATES (PARALLEL)               │
├─────────────────────────────────────────────────┤
│ File: performance/index_manager.py             │
│ Process:                                        │
│  ├─ Insert into vector index                   │
│  ├─ Insert into keyword index (BM25)           │
│  ├─ Update temporal index                      │
│  └─ Update entity importance indices           │
│ Time: <20ms (parallel batch)                   │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ STEP 9: CACHE INVALIDATION                     │
├─────────────────────────────────────────────────┤
│ File: performance/query_cache.py               │
│ Process:                                        │
│  ├─ Invalidate affected cache entries          │
│  ├─ Queue related queries for re-computation   │
│  └─ Update cache statistics                    │
│ Time: <5ms                                      │
└─────────────────────────────────────────────────┘
    ↓
SUCCESS CONFIRMATION TO AGENT
Total Ingestion Time: 145-180ms
(Agent doesn't wait; async processing continues in background)
```

---

### 2.2 RETRIEVAL PIPELINE (RECALL Operation)

```
AGENT REQUEST (with Recall Profile)
    │
    ├─ Query: "Show me authentication patterns"
    ├─ Depth: 3 (Experiential + Contextual + Abstract)
    ├─ Breadth: 50
    ├─ Reasoning Type: "Causal"
    ├─ Temporal Scope: "6 months"
    └─ Confidence Threshold: 0.8
    ↓
┌──────────────────────────────────────────────────────┐
│ STEP 1: REQUEST PARSING & OPTIMIZATION              │
├──────────────────────────────────────────────────────┤
│ File: recall_engine.py / query_optimizer.py         │
│ Process:                                             │
│  ├─ Parse recall profile                            │
│  ├─ Determine retrieval strategy based on params    │
│  ├─ Build query execution plan (which indices, etc) │
│  ├─ Check if cached result exists (hit → return)   │
│  └─ Set timeout budgets per retrieval path          │
│ Time: <5ms                                           │
└──────────────────────────────────────────────────────┘
    ↓ (PARALLEL EXECUTION OF 3 PATHS)
    │
    ├─────────────────────┬─────────────────────┬────────────────────┐
    ↓                     ↓                     ↓                    ↓
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ PATH 1:          │ │ PATH 2:          │ │ PATH 3:          │ │ STEP 2: QUERY    │
│ SEMANTIC SEARCH  │ │ GRAPH TRAVERSAL  │ │ TEMPORAL SEARCH  │ │ ORCHESTRATION    │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ File:            │ │ File:            │ │ File:            │ │ File:            │
│ retrieval/       │ │ retrieval/       │ │ retrieval/       │ │ retrieval/       │
│ semantic_*.py    │ │ graph_*.py       │ │ temporal_*.py    │ │ multi_path_*.py  │
│                  │ │                  │ │                  │ │                  │
│ Process:         │ │ Process:         │ │ Process:         │ │ Process:         │
│ ├─ Embed query   │ │ ├─ Extract       │ │ ├─ Filter by     │ │ ├─ Launch all    │
│ ├─ Vector search │ │ │ entity refs    │ │ │ temporal window │ │ │ 3 retrievals    │
│ │ (HNSW algo)   │ │ ├─ Start graph   │ │ ├─ Sort by       │ │ │ concurrently    │
│ ├─ Rank by      │ │ │ traversal from  │ │ │ recency        │ │ ├─ Wait for all  │
│ │ similarity    │ │ │ found entities  │ │ ├─ Apply         │ │ │ to complete or  │
│ ├─ Apply        │ │ ├─ Traverse K hops│ │ │ confidence      │ │ │ timeout         │
│ │ filters       │ │ ├─ Limit fan-out │ │ │ filter         │ │ └─ Time: 40-60ms │
│ │ (confidence,  │ │ │ (max 50 per hop)│ │ └─ Return ranked │ │                  │
│ │ recency)      │ │ ├─ Rank by path  │ │   results       │ │                  │
│ └─ Return top   │ │ │ relevance      │ │                 │ │                  │
│   N results     │ │ └─ Return all    │ │                 │ │                  │
│                  │ │   found neighbors│ │                 │ │                  │
│ Time: 20-30ms   │ │                  │ │                 │ │                  │
│ (vector index)  │ │ Time: 30-40ms    │ │ Time: 10-15ms   │ │                  │
│                  │ │ (graph traversal)│ │ (temporal index)│ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘
    │                     │                     │
    └─────────────────────┴─────────────────────┘
                  ↓
┌──────────────────────────────────────────────────────┐
│ STEP 3: RESULT DEDUPLICATION                        │
├──────────────────────────────────────────────────────┤
│ File: retrieval/multi_path_coordinator.py           │
│ Process:                                             │
│  ├─ Merge results from 3 paths                      │
│  ├─ Remove duplicates (same memory found via diff   │
│  │ paths)                                           │
│  ├─ Mark which paths found each result              │
│  └─ Preserve all path information for transparency  │
│ Time: <5ms                                           │
└──────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────┐
│ STEP 4: MULTI-DIMENSIONAL RANKING                   │
├──────────────────────────────────────────────────────┤
│ File: ranking/fusion_ranker.py                      │
│ Process:                                             │
│  ├─ Score by reasoning-type fit (causal_reasoner)  │
│  ├─ Apply recency weighting (temporal decay)       │
│  ├─ Factor in confidence scores                     │
│  ├─ Weight path agreements (found by multiple paths)│
│  ├─ Apply breadth constraints (top N results)      │
│  └─ Final composite score: weighted fusion          │
│ Scoring Formula:                                     │
│  score = α×semantic_score +                         │
│          β×graph_score +                            │
│          γ×temporal_score +                         │
│          δ×reasoning_fit_score +                    │
│          ε×confidence_score                         │
│  where α,β,γ,δ,ε vary by reasoning_type            │
│ Time: <10ms (vectorized operations)                │
└──────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────┐
│ STEP 5: BREADTH EXPANSION (OPTIONAL)                │
├──────────────────────────────────────────────────────┤
│ File: retrieval/context_retriever.py                │
│ Process (if breadth > focused):                     │
│  ├─ For each top result, find neighbors            │
│  ├─ Add supporting facts                            │
│  ├─ Add contradicting facts                         │
│  ├─ Add related contexts                            │
│  └─ Maintain hierarchical structure                │
│ Time: <20ms (if requested)                         │
└──────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────┐
│ STEP 6: PROVENANCE ATTACHMENT                       │
├──────────────────────────────────────────────────────┤
│ File: models/memory_result.py                       │
│ Process:                                             │
│  ├─ For each result, attach:                        │
│  │  ├─ Why it was retrieved (which path(s))        │
│  │  ├─ Confidence level                            │
│  │  ├─ Related memories                            │
│  │  ├─ Contradictions (if any)                     │
│  │  └─ Supporting evidence                         │
│  ├─ Build query plan explanation                    │
│  └─ Include retrieval latency breakdown            │
│ Time: <5ms                                           │
└──────────────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────────────┐
│ STEP 7: RESULT CACHING                              │
├──────────────────────────────────────────────────────┤
│ File: performance/query_cache.py                    │
│ Process:                                             │
│  ├─ Generate cache key from query profile           │
│  ├─ Store results with TTL (based on stratum ages)  │
│  ├─ Invalidate if any underlying memory changes     │
│  └─ Update cache hit/miss statistics                │
│ Time: <2ms                                           │
└──────────────────────────────────────────────────────┘
    ↓
RESULT RETURNED TO AGENT
    ↓
Result Format:
{
  "results": [
    {
      "memory_id": "...",
      "content": "...",
      "final_score": 0.95,
      "layer": "CONTEXTUAL",
      "paths_found": ["semantic", "graph"],
      "confidence": 0.92,
      "provenance": "Found via semantic + graph traversal",
      "supporting_facts": [...],
      "contradictions": [...],
      "related_contexts": [...]
    },
    ...
  ],
  "query_plan": "3-layer search with 50-node breadth expansion",
  "execution_time_ms": 87,
  "cache_hit": false,
  "total_coverage": 0.89
}

Total Query Latency: 60-90ms (95th percentile < 150ms)
```

---

## 3. CORE ALGORITHMS

### 3.1 MULTI-PATH PARALLEL RETRIEVAL ALGORITHM

**Algorithm: Parallel Adaptive Retrieval Fusion (PARF)**

```
INPUT: Query Q, RecallProfile (depth, breadth, reasoning_type)
OUTPUT: RankedResults with provenance

FUNCTION PARF(Query Q, RecallProfile RP):
    
    // Initialize
    queryPlan ← OptimizeQueryPlan(Q, RP)
    timeout ← CalculateTimeout(RP)
    
    // PATH 1: Semantic Vector Search
    PARALLEL:
        semanticResults ← VectorSearch(
            query_embedding: Embed(Q),
            num_results: RP.breadth × 2,
            filters: [confidence ≥ RP.threshold],
            time_range: RP.temporal_scope
        )
        semanticScores ← [HNSW similarity scores]
    
    // PATH 2: Graph Relationship Traversal
    PARALLEL:
        entities ← EntityExtraction(Q)
        startNodes ← GraphSearch(entities)
        graphResults ← MultiHopTraversal(
            start_nodes: startNodes,
            max_depth: RP.depth,
            max_fan_out: 50,
            breadth: RP.breadth
        )
        graphScores ← [Path relevance + relationship strength]
    
    // PATH 3: Temporal Filtering
    PARALLEL:
        temporalResults ← TemporalIndexQuery(
            time_range: RP.temporal_scope,
            sort_by: recency,
            filters: [confidence ≥ RP.threshold]
        )
        temporalScores ← [Recency-weighted relevance]
    
    // Wait for all paths (or timeout)
    WAIT_FOR_ALL(semanticResults, graphResults, temporalResults, timeout)
    
    // Deduplicate
    allResults ← DEDUPLICATE(
        semanticResults ∪ graphResults ∪ temporalResults
    )
    
    // Multi-dimensional ranking
    FOR EACH result IN allResults:
        reasoning_fit ← ReasoningTypeRanker(result, RP.reasoning_type)
        recency_weight ← RecencyRanker(result.timestamp)
        path_agreement ← COUNT(paths where result found) / 3
        
        final_score ← WEIGHTED_SUM(
            semantic_score: result.semantic_score × α,
            graph_score: result.graph_score × β,
            temporal_score: result.temporal_score × γ,
            reasoning_fit: reasoning_fit × δ,
            path_agreement: path_agreement × ε,
            confidence: result.confidence × ζ
        )
        
        result.final_score ← final_score
    
    // Sort and limit by breadth
    sortedResults ← SORT(allResults by final_score DESC)
    topResults ← sortedResults[0:RP.breadth]
    
    // Optional breadth expansion
    IF RP.breadth > THRESHOLD:
        FOR EACH result IN topResults:
            result.supporting_facts ← GetNeighbors(result, "supporting")
            result.contradictions ← GetNeighbors(result, "contradicting")
            result.related_contexts ← GetNeighbors(result, "context")
    
    // Attach provenance
    FOR EACH result IN topResults:
        result.paths_found ← FILTER(
            ["semantic", "graph", "temporal"],
            path → result found via path
        )
        result.provenance ← ExplainResult(result, queryPlan)
    
    RETURN topResults with provenance

END FUNCTION
```

**Complexity Analysis:**
- Semantic path: O(d × log n) where d=embedding dims, n=vectors
- Graph path: O(k^h) where k=fan-out, h=depth (limited to k=50, h=3)
- Temporal path: O(log n) with range filter
- Ranking: O(m log m) where m=total results before limiting
- Overall: O(m log m) with early termination via timeout

---

### 3.2 HIERARCHICAL GRAPH TRAVERSAL ALGORITHM

**Algorithm: Adaptive K-Hop Limited Traversal (AKHLT)**

```
INPUT: StartNodes[], MaxHops H, FanOutLimit F, BreadthLimit B
OUTPUT: ExpandedGraph with relationship scoring

FUNCTION AKHLT(startNodes[], H, F, B):
    
    visitedNodes ← SET()
    resultNodes ← PRIORITY_QUEUE(by relevance)
    currentFrontier ← startNodes
    currentHop ← 0
    
    WHILE currentHop < H AND currentFrontier NOT EMPTY:
        
        nextFrontier ← []
        
        FOR EACH node IN currentFrontier:
            IF node IN visitedNodes:
                CONTINUE
            
            visitedNodes.ADD(node)
            
            // Get neighbors (limited by fan-out)
            neighbors ← GetNeighbors(
                node,
                max_count: F,
                sort_by: edge_weight
            )
            
            FOR EACH (neighbor, edgeType, weight) IN neighbors:
                
                // Score this path
                pathRelevance ← CalculatePathRelevance(
                    start_node: startNodes[0],
                    current_node: node,
                    target_node: neighbor,
                    hops_taken: currentHop + 1,
                    edge_weight: weight
                )
                
                // Only include if meets relevance threshold
                IF pathRelevance > THRESHOLD:
                    resultNodes.ADD(
                        (neighbor, pathRelevance, currentHop + 1)
                    )
                    nextFrontier.ADD(neighbor)
        
        currentFrontier ← nextFrontier
        currentHop ← currentHop + 1
        
        // Prune if expanding beyond limit
        IF resultNodes.size > B:
            resultNodes ← TOP_K(resultNodes, B)
    
    RETURN resultNodes

END FUNCTION
```

**Path Relevance Scoring:**
```
pathRelevance(start, current, target, hops, weight) =
    (similarity(start, target) × weight) /
    (1 + λ × hops)  // Decay by hops

where λ controls depth penalty (typically λ=0.2)
```

---

### 3.3 REASONING-TYPE ADAPTIVE RANKING ALGORITHM

**Algorithm: Contextual Ranking Adaptation (CRA)**

```
INPUT: Results[], ReasoningType RT
OUTPUT: ReasoningTypeScores

FUNCTION CRA(Results[], RT):
    
    scores ← EMPTY_DICT
    
    SWITCH RT:
        
        CASE "DESCRIPTIVE":  // What? When? Who?
            FOR EACH result IN Results:
                // Prioritize recent, high-confidence facts
                recency ← NormalizeScore(
                    1 / (1 + age_in_days/7)  // Decay over week
                )
                confidence ← result.confidence
                directness ← 1 if result.layer = EXPERIENTIAL else 0.7
                
                scores[result] ← 
                    0.4×recency + 0.4×confidence + 0.2×directness
        
        CASE "CAUSAL":  // Why? What causes?
            FOR EACH result IN Results:
                // Prioritize principles and causal chains
                is_causal ← 1 if result has CAUSES edges else 0
                evidence_count ← COUNT(supporting_facts)
                layer_value ← {
                    ABSTRACT: 1.0,
                    CONTEXTUAL: 0.6,
                    EXPERIENTIAL: 0.3
                }[result.layer]
                
                scores[result] ←
                    0.4×is_causal + 0.3×evidence_count + 0.3×layer_value
        
        CASE "EVALUATIVE":  // Is this good? Success?
            FOR EACH result IN Results:
                // Prioritize outcomes and success indicators
                has_outcome ← 1 if result has OUTCOME properties else 0
                success_rate ← CalculateSuccessRate(result)
                feedback_quality ← NormalizeFeedbackQuality(result)
                
                scores[result] ←
                    0.4×has_outcome + 0.3×success_rate + 0.3×feedback_quality
        
        CASE "PROCEDURAL":  // How? Steps?
            FOR EACH result IN Results:
                // Prioritize successful procedures and recent versions
                is_procedure ← 1 if result is process-like else 0
                success_rate ← CalculateSuccessRate(result)
                recency ← NormalizeScore(1 / (1 + age_in_days/30))
                
                scores[result] ←
                    0.4×is_procedure + 0.3×success_rate + 0.3×recency
        
        CASE "COMPARATIVE":  // Which? Trade-offs?
            FOR EACH result IN Results:
                // Prioritize alternatives and trade-off information
                has_alternatives ← COUNT(similar_results_exploring_same_space)
                tradeoff_clarity ← CalculateTradeoffClarity(result)
                completeness ← 1 if has alternatives else 0.5
                
                scores[result] ←
                    0.4×has_alternatives + 0.3×tradeoff_clarity + 0.3×completeness
        
        CASE "STRATEGIC":  // What should we? Vision?
            FOR EACH result IN Results:
                // Prioritize goals, constraints, and long-term implications
                is_strategic ← 1 if result.layer = ABSTRACT else 0.5
                goal_relevance ← CalculateGoalAlignment(result)
                scope ← result.impact_scope / max_scope
                
                scores[result] ←
                    0.4×is_strategic + 0.3×goal_relevance + 0.3×scope
        
        CASE "CREATIVE":  // What if? Novel?
            FOR EACH result IN