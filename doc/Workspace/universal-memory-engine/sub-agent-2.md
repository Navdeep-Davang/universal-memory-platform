# Sub-Agent 2: Conflict Detection & Resolution

## Your Assignment
- **Orchestration:** universal-memory-engine
- **Current Cycle:** CYCLE-4
- **Status:** READY

## Strategic Context & Prompts
### Master Agent Guidance:
You are responsible for the engine's ability to handle contradictions—the unique "Cognitive" feature of our platform.
- **Contradiction Detection:** When new memories are added, identify if they contradict existing ones using vector similarity + LLM verification.
- **Resolution Engine:** Create a structured way to track, analyze, and resolve these conflicts (Manual or Automated).
- **Graph Consistency:** Use the `CONFLICTS_WITH` relationship to maintain a non-linear memory history.

## Scope & Constraints
### What You Own:
- `src/conflict_resolution/` (contradiction_detector.py, conflict_analyzer.py, resolution_engine.py)
- `src/operations/contradict_operation.py`
- `src/api/rest_api.py` (Conflict resolution endpoints: `/api/conflicts/*`)
- `src/models/edges.py` (Update relationship status fields if needed)

### What You DON'T Touch:
- `sdk/python/` (Owned by Sub-Agent 1)
- `dashboard/` (Owned by Sub-Agent 3)
- `src/core/recall_engine.py` (Logic stabilized)

## Your Tasks
### Phase 6: Conflict Detection System
- [ ] **Task 6.1: Contradiction Detector**
    - [ ] Implement `src/conflict_resolution/contradiction_detector.py`.
    - [ ] Use vector search to find candidate conflicts.
    - [ ] Implement LLM-based verification to distinguish between actual contradictions and different contexts.
- [ ] **Task 6.2: Conflict Analyzer**
    - [ ] Implement `src/conflict_resolution/conflict_analyzer.py`.
    - [ ] Categorize conflict severity and suggest resolution strategies.
- [ ] **Task 6.3: Resolution Engine**
    - [ ] Implement `src/conflict_resolution/resolution_engine.py`.
    - [ ] Manage `CONFLICTS_WITH` edges and resolution metadata (status, notes).
- [ ] **Task 6.4: Contradict Operation**
    - [ ] Implement `src/operations/contradict_operation.py` as a unified workflow.
- [ ] **Task 6.5: Conflict API Endpoints**
    - [ ] Implement `PUT /api/conflicts/{id}/resolve` and `GET /api/conflicts`.

## Progress Tracking
- **Overall Completion:** 0%
- **Current Task:** T6.1
- **Last Update:** 2026-01-08

## Implementation Checklist
- [ ] Logic implemented as per Strategic Context
- [ ] LLM prompts for contradiction detection are high-precision
- [ ] Conflict resolution state machine is clear (pending -> resolved -> overridden)
- [ ] API endpoints follow REST conventions
- [ ] Verification performed
- [ ] Ready for Master QA
