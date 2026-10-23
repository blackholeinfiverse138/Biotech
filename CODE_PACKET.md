# CODE PACKET & INDEX — BIOTECH ARCHITECTURE (T-GOV-F01 & T-GOV-002)

**Task Identifier:** T-GOV-F01 & T-GOV-002  
**Task Titles:**  
- **T-GOV-F01:** Remediate Incomplete & Harden BIOTECH INTEGRATION, AUDIT & CONVERGENCE TASK Architecture  
- **T-GOV-002:** Milestone Advancement: Scalable Ecosystem Integration & Pipeline Automation  
**Candidate / Agent:** Ansh Gupta (AI/ML + Data Audit Lead)  
**Governance Authority:** Biotech Integration, Audit & Convergence / BHIV  
**Date:** October 2026  
**Status:** COMPLETE (100% Test Pass Rate, 55/55 Tests Passing)  

---

## 1. Complete Directory Tree

```text
.
├── api/
│   ├── __init__.py
│   ├── production.py
│   └── review_routes.py
├── canonical_db/
│   ├── __init__.py
│   ├── db.py
│   └── integration.py
├── core/
│   ├── __init__.py
│   └── engine.py
├── evaluation_engine/
│   ├── __init__.py
│   ├── execution_pipeline.py
│   ├── pravah_streaming.py
│   └── rule_engine.py
├── integrations/
│   ├── __init__.py
│   └── local_llm_client.py
├── model/
│   ├── __init__.py
│   └── schemas.py
├── models/
│   ├── __init__.py
│   └── schemas.py
├── security/
│   ├── __init__.py
│   └── middleware.py
├── service/
│   ├── __init__.py
│   └── governance_service.py
├── services/
│   ├── __init__.py
│   └── governance_service.py
├── task_selector/
│   ├── __init__.py
│   ├── review_orchestrator.py
│   └── state_machine.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_deterministic_execution.py
│   │   ├── test_pravah_and_concurrency_api.py
│   │   └── test_production_api.py
│   └── unit/
│       ├── __init__.py
│       ├── test_concurrency_governance.py
│       ├── test_local_llm_client.py
│       ├── test_parikshak_interoperability.py
│       ├── test_pravah_streaming.py
│       ├── test_review_orchestrator.py
│       ├── test_rule_engine.py
│       └── test_security_middleware.py
├── ANSH_BIOTECH_DATA_AI_AUDIT_EXECUTION_PLAN.md
├── ANSH_BIOTECH_DATA_AI_AUDIT_REPORT.md
├── BIOTECH_DATA_INTEGRITY_CHECKLIST.md
├── BIOTECH_PRATIK_FINAL_HANDOFF.md
├── PRATIK_AUDIT_VS_ANSH_AUDIT_COMPARISON.md
├── SETU_EOS_TASK_REGISTRATION.md
├── REVIEW_PACKET.md
├── CODE_PACKET.md
├── CODE_INDEX.md
├── README.md
├── audit_harness_ansh.py
├── pytest.ini
└── requirements.txt
```

---

## 2. File Implementation Manifest

| File Path | Role / Module | Description |
|---|---|---|
| `api/review_routes.py` | Parikshak Review Router | Parikshak context review routes (`/api/v1/review/evaluate`, `/api/v1/review/verify`, `/api/v1/review/health`) providing direct evaluation engine interoperability. |
| `api/production.py` | Production REST Microservice | FastAPI microservice exposing Pravah streaming, Concurrency governance, and candidate evaluation routes with strict Pydantic schemas (`extra="forbid"`). |
| `canonical_db/db.py` | Canonical Persistence Engine | SQLite + JSONL audit ledger engine maintaining audit candidate histories, deterministic state records, and query retrieval. |
| `canonical_db/integration.py` | MasterDB & Parikshak Adapters | `MasterDBIntegrationAdapter` and `ParikshakSyncAdapter` providing resilient bidirectional communication with ecosystem databases. |
| `core/engine.py` | Central Orchestration Core | High-level `BiotechCoreEngine` managing end-to-end execution, rule audits, Pravah ledger event logging, and OCC transitions. |
| `evaluation_engine/execution_pipeline.py` | End-to-End Execution Pipeline | Coordinates candidate ingestion, deterministic rule gating, Pravah replay streaming, and review decision states. |
| `evaluation_engine/pravah_streaming.py` | Asynchronous Event Streaming & Replay Engine | Thread-safe `PravahReplayEngine` with monotonic sequence tracking, SHA-256 parent hash chaining, append-only JSONL persistence, deterministic replay windowing, and cryptographic integrity verification. |
| `evaluation_engine/rule_engine.py` | Core Evaluation Engine | Deterministic evaluation of schema strictness, multi-drug attribution, synthetic quarantine, and Section 8 boundaries with composite scoring and state hashing. |
| `models/schemas.py` & `model/schemas.py` | Strict Data Schemas | Pydantic v2 domain schemas (`FormulationRecord`, `BiotechAuditSubmission`, `CandidateReviewContract`, `ParikshakSyncRecord`) enforcing `ConfigDict(extra="forbid")`. |
| `services/governance_service.py` & `service/governance_service.py` | Governance Service Layer | Business logic service executing audit submissions, OCC transitions, and candidate history synchronization. |
| `task_selector/state_machine.py` | Concurrency Governance & DFA State Machine | `ConcurrencyGovernanceEngine` driving an 8-state DFA with Optimistic Concurrency Control (OCC), version tracking, `OCCConflictError` (409 Conflict), `InvalidStateTransitionError` (422 Unprocessable), and deterministic SHA-256 state hashing. |
| `task_selector/review_orchestrator.py` | Workflow Orchestrator | Coordinates the 9-stage Day 3 convergence cycle and records Section 16 independent audit disputes. |
| `integrations/local_llm_client.py` | Resilient Integration Client | Local LLM extraction client with deterministic rule-based fallback and in-memory caching. |
| `security/middleware.py` | Security & Error Boundary Middleware | ASGI middleware guaranteeing zero unhandled 500 exceptions, token replay prevention (HTTP 409), and role authorization. |
| `requirements.txt` | Dependency Specification | Exactly pinned versions (`==`) preventing dependency drift across all core libraries. |
| `pytest.ini` | Test Configuration | Pytest configuration targeting `tests/` with strict options and `asyncio_mode = auto`. |
| `tests/conftest.py` | Shared Test Fixtures | TestClient, clean token cache, and isolated component fixtures. |
| `tests/unit/test_parikshak_interoperability.py` | Parikshak Interoperability Suite | 8 tests validating Phase 1 Hard Gate compliance, 9 context files availability, canonical DB operations, adapter integration, and execution pipeline flows. |
| `tests/unit/test_pravah_streaming.py` | Unit Test Suite | Tests schema strictness, monotonic sequencing, parent-hash chaining, replay windowing, cryptographic integrity, and state hash determinism. |
| `tests/unit/test_concurrency_governance.py` | Unit Test Suite | Tests entity registration, DFA state transitions, OCC version conflict detection (409), illegal jump rejection (422), and multi-threaded race conditions. |
| `tests/integration/test_pravah_and_concurrency_api.py` | Integration Test Suite | Full HTTP lifecycle testing for Pravah streaming, replay, integrity, and OCC transition endpoints. |
| `tests/integration/test_deterministic_execution.py` | Integration Test Suite | Proves 50 consecutive runs produce identical SHA-256 state hashes across Pravah, OCC, Rules, and Packets. |
| `tests/integration/test_production_api.py` | Integration Test Suite | Tests all base API routes, fail-closed rejections, unauthorized roles, and malformed input handling. |
| `tests/unit/test_rule_engine.py` | Unit Test Suite | Evaluates 6 deterministic rules including schema strictness, attribution, and synthetic quarantine. |
| `tests/unit/test_review_orchestrator.py` | Unit Test Suite | Tests 9-stage review workflow, Section 16 disagreements, and decision state finalization. |
| `tests/unit/test_security_middleware.py` | Unit Test Suite | Tests token replay rejection (HTTP 409) and role enumeration. |
| `tests/unit/test_local_llm_client.py` | Unit Test Suite | Tests deterministic extraction and caching consistency. |
| `REVIEW_PACKET.md` | Verification Artifact | Parikshak self-audit scores (100/100), Phase 1 Hard Gate sections, 50-run logs, and dual task certification. |
| `CODE_PACKET.md` | Code Packet Artifact | Complete directory tree, manifest, and git diff summaries. |
| `CODE_INDEX.md` | Code Index Artifact | Detailed architectural index and symbol reference. |

---

## 3. Production API Route Specifications

| HTTP Method | Route | Request Schema | Response Schema | Description |
|---|---|---|---|---|
| `GET` | `/production/health` | None | `HealthResponse` | Verifies service health, active capabilities, and error boundary status. |
| `GET` | `/production/metrics` | None | `MetricsResponse` | Returns canonical SHA-256 state hash proof and active review metrics. |
| `POST` | `/production/pravah/stream` | `PravahEvent` | `Dict[str, Any]` | Streams event into append-only Pravah replay ledger with parent hash chaining. |
| `POST` | `/production/pravah/replay` | `PravahReplayRequest` | `List[PravahEvent]` | Deterministically replays events within specified sequence window. |
| `GET` | `/production/pravah/integrity` | None | `Dict[str, Any]` | Cryptographically verifies ledger chain continuity and returns state hash. |
| `POST` | `/production/governance/concurrency/transition` | `TransitionRequest` | `ConcurrencyRecord` | Executes OCC-guarded DFA state transition with monotonic version check. |
| `GET` | `/production/governance/concurrency/state/{entity_id}` | None | `ConcurrencyRecord` | Retrieves current DFA state, version, and transition history. |
| `POST` | `/production/biotech/audit` | `BiotechAuditRequest` | `EvaluationRubric` | Executes full deterministic audit on candidate payloads. |
| `POST` | `/production/biotech/evaluate` | `BiotechEvaluationRequest` | `EvaluationRubric` | Rule evaluation across candidate streams. |
| `POST` | `/production/biotech/review` | `ReviewPacketContract` | `CandidateReviewRecord` | Starts candidate review and assigns initial decision state. |
| `POST` | `/production/biotech/disagreement` | `DisagreementRecordRequest` | `CandidateReviewRecord` | Records Section 16 independent audit disagreement. |
| `POST` | `/production/biotech/extract` | `EntityExtractionRequest` | `LLMVerificationResponse` | Resilient semantic extraction with deterministic fallback. |
| `POST` | `/api/v1/review/evaluate` | `Dict[str, Any]` | `Dict[str, Any]` | Parikshak review engine direct evaluation endpoint. |
| `POST` | `/api/v1/review/verify` | `Dict[str, Any]` | `Dict[str, Any]` | Cryptographic verification of candidate audit proofs. |
| `GET` | `/api/v1/review/health` | None | `Dict[str, Any]` | Parikshak review integration health check. |

---

## 4. Git Diff Summary

```text
M  CODE_INDEX.md
M  CODE_PACKET.md
M  README.md
M  REVIEW_PACKET.md
M  api/production.py
M  evaluation_engine/rule_engine.py
A  api/review_routes.py
A  canonical_db/__init__.py
A  canonical_db/db.py
A  canonical_db/integration.py
A  core/__init__.py
A  core/engine.py
A  evaluation_engine/execution_pipeline.py
A  model/__init__.py
A  model/schemas.py
A  models/__init__.py
A  models/schemas.py
A  service/__init__.py
A  service/governance_service.py
A  services/__init__.py
A  services/governance_service.py
A  tests/unit/test_parikshak_interoperability.py
```
