# CODE INDEX — BIOTECH ARCHITECTURE (T-GOV-002)

**Task Identifier:** T-GOV-002  
**Task Title:** Milestone Advancement: Scalable Ecosystem Integration & Pipeline Automation  
**Candidate / Agent:** Ansh Gupta (AI/ML + Data Audit Lead)  
**Governance Authority:** Biotech Integration, Audit & Convergence / BHIV  
**Date:** October 2026  
**Status:** COMPLETE (100% Test Pass Rate, 47/47 Tests Passing)  

---

## 1. Architectural Component Index

### `evaluation_engine/pravah_streaming.py`
- `class PravahEvent(BaseModel)`: Immutable event data model with `extra="forbid"`, sequence counter, SHA-256 parent hash, and cryptographic payload signature.
- `class PravahReplayEngine`: Append-only, thread-safe (`RLock`) streaming engine managing replay windows, monotonic sequences, parent-hash chains, and ledger state hashing.
  - `stream_event(event_type, payload, entity_id)`: Appends an event to the ledger, computing parent link.
  - `replay_events(from_sequence, to_sequence)`: Returns ordered events within sequence bounds.
  - `verify_integrity()`: Validates cryptographic chain continuity from genesis.
  - `compute_ledger_state_hash()`: Computes deterministic SHA-256 state hash of the entire ledger.

### `task_selector/state_machine.py`
- `class GovernanceState(str, Enum)`: 8-state DFA: `INIT`, `VALIDATING`, `AUDITED`, `CONVERGED`, `CERTIFIED`, `QUARANTINED`, `REJECTED`, `DISPUTED`.
- `class ConcurrencyRecord(BaseModel)`: Entity concurrency tracker with current state, integer version, and transition audit history.
- `class ConcurrencyGovernanceEngine`: Thread-safe OCC manager.
  - `register_entity(entity_id, initial_state)`: Registers a new entity with version 1.
  - `transition_state(entity_id, expected_version, target_state, actor, reason)`: Validates OCC version (raises `OCCConflictError` on mismatch) and DFA transition legality (raises `InvalidStateTransitionError` on illegal jump). Monotonically increments version.
  - `compute_governance_state_hash()`: Computes deterministic SHA-256 fingerprint of all managed entities.

### `api/production.py`
- Microservice routing engine implementing strict Pydantic schemas, role authorization, and unified error boundary:
  - `/production/health`: Health status and system capability verification.
  - `/production/metrics`: Active review metrics and canonical SHA-256 hash.
  - `/production/pravah/stream`: Ingests event into append-only ledger.
  - `/production/pravah/replay`: Replays event stream across sequence intervals.
  - `/production/pravah/integrity`: Validates ledger chain integrity.
  - `/production/governance/concurrency/transition`: OCC-guarded DFA state transition.
  - `/production/governance/concurrency/state/{entity_id}`: Retrieves entity version and state.
  - `/production/biotech/audit`: Full deterministic audit against 6 core rules.
  - `/production/biotech/evaluate`: Rule evaluation across candidate streams.
  - `/production/biotech/review`: 9-stage convergence workflow review.
  - `/production/biotech/disagreement`: Section 16 independent audit disagreement registration.
  - `/production/biotech/extract`: Resilient semantic extraction with deterministic fallback.

### `security/middleware.py`
- `class ErrorBoundaryMiddleware(BaseHTTPMiddleware)`: Traps all uncaught exceptions, preventing any 500 status codes and returning structured error payloads with trace IDs.
- `class TokenReplayCache`: In-memory thread-safe replay cache preventing duplicate token usage (HTTP 409).
- `require_role(required_role)`: FastAPI dependency enforcing role-based access control.

### `evaluation_engine/rule_engine.py`
- `class RuleEngine`: Enforces 6 deterministic Biotech evaluation rules:
  - Strict schema compliance and fail-closed null checks.
  - Multi-drug attribution verification.
  - Synthetic dataset quarantine.
  - Scientific boundary checks.
  - Conflict preservation tracking.
  - Deterministic SHA-256 state hashing.

### `task_selector/review_orchestrator.py`
- `class ReviewOrchestrator`: Manages candidate reviews across the 9-stage Day 3 convergence lifecycle and registers Section 16 disagreement entries.

### `integrations/local_llm_client.py`
- `class LocalLLMClient`: Offline deterministic fallback semantic entity extractor and red-flag detector.

---

## 2. Test Suite Mapping

| Test File | Target Module | Test Count | Key Invariants Tested |
|---|---|---|---|
| `tests/unit/test_pravah_streaming.py` | `pravah_streaming.py` | 5 | Strict schema, monotonic sequencing, replay windowing, cryptographic integrity, determinism |
| `tests/unit/test_concurrency_governance.py` | `state_machine.py` | 5 | Registration, valid DFA transitions, OCC conflict detection (409), illegal transition rejection (422), race conditions |
| `tests/unit/test_rule_engine.py` | `rule_engine.py` | 13 | 6 deterministic rules, schema strictness, fail-closed handling, quarantine, state hash |
| `tests/unit/test_review_orchestrator.py` | `review_orchestrator.py` | 4 | Review flow, Section 16 disagreement recording, stage advancement, decision state |
| `tests/unit/test_security_middleware.py` | `middleware.py` | 2 | Replay cache prevention (409), role authorization enumeration |
| `tests/unit/test_local_llm_client.py` | `local_llm_client.py` | 2 | Deterministic rule-based extraction, caching consistency |
| `tests/integration/test_pravah_and_concurrency_api.py` | `production.py` | 6 | End-to-end HTTP tests for Pravah streaming, replay, integrity, and OCC transitions |
| `tests/integration/test_production_api.py` | `production.py` | 7 | Health, metrics, audit, evaluate, review, disagreement, error boundary |
| `tests/integration/test_deterministic_execution.py` | All Engines | 3 | 50 consecutive runs producing identical SHA-256 state hashes |
| **Total** | | **47** | **100% Pass Rate** |
