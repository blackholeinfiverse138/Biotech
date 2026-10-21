# CODE PACKET & INDEX — BIOTECH ARCHITECTURE (T-GOV-F01)

**Task Identifier:** T-GOV-F01  
**Candidate:** Ansh Gupta (AI/ML + Data Audit Lead)  
**Repository:** `blackholeinfiverse138/Biotech`  
**Date:** October 2026  
**Status:** COMPLETE  

---

## 1. Complete Directory Tree

```text
.
├── api/
│   ├── __init__.py
│   └── production.py
├── evaluation_engine/
│   ├── __init__.py
│   └── rule_engine.py
├── integrations/
│   ├── __init__.py
│   └── local_llm_client.py
├── security/
│   ├── __init__.py
│   └── middleware.py
├── task_selector/
│   ├── __init__.py
│   └── review_orchestrator.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_deterministic_execution.py
│   │   └── test_production_api.py
│   └── unit/
│       ├── __init__.py
│       ├── test_local_llm_client.py
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
├── README.md
├── audit_harness_ansh.py
├── pytest.ini
└── requirements.txt
```

---

## 2. File Implementation Manifest

| File Path | Role / Module | Lines | Description |
|---|---|---|---|
| `api/production.py` | Production REST API | 275 | FastAPI production microservice with strict Pydantic schemas, role-based auth, and error boundary. |
| `evaluation_engine/rule_engine.py` | Core Evaluation Engine | 280 | Deterministic evaluation of schema strictness, multi-drug attribution, synthetic quarantine, and Section 8 boundaries. |
| `task_selector/review_orchestrator.py` | Workflow Orchestrator | 215 | Coordinates the 9-stage Day 3 convergence cycle and records Section 16 independent audit disputes. |
| `integrations/local_llm_client.py` | Resilient Integration Client | 125 | Local LLM extraction client with deterministic rule-based fallback and in-memory caching. |
| `security/middleware.py` | Security & Error Boundary | 120 | Intercepts unhandled exceptions (zero 500s), enforces token replay protection, and user roles. |
| `requirements.txt` | Dependency Specification | 9 | Exactly pinned versions (`==`) preventing dependency drift. |
| `pytest.ini` | Test Configuration | 7 | Pytest configuration targeting `tests/` with strict options. |
| `tests/conftest.py` | Shared Test Fixtures | 35 | TestClient, clean token cache, and component fixtures. |
| `tests/unit/test_rule_engine.py` | Unit Test Suite | 130 | Evaluates 6 deterministic rules including schema strictness, attribution, and synthetic quarantine. |
| `tests/unit/test_review_orchestrator.py` | Unit Test Suite | 90 | Tests 9-stage review workflow, Section 16 disagreements, and decision state finalization. |
| `tests/unit/test_security_middleware.py` | Unit Test Suite | 40 | Tests token replay rejection (HTTP 409) and role enumeration. |
| `tests/unit/test_local_llm_client.py` | Unit Test Suite | 35 | Tests deterministic extraction and caching consistency. |
| `tests/integration/test_production_api.py` | Integration Test Suite | 115 | Tests all API routes, fail-closed rejections, unauthorized roles, and malformed input handling. |
| `tests/integration/test_deterministic_execution.py`| Integration Test Suite | 45 | Proves 50 consecutive runs produce identical SHA-256 state hashes. |
| `REVIEW_PACKET.md` | Verification Artifact | 180 | Parikshak self-audit scores, 50-run logs, and architectural proofs. |

---

## 3. Production API Route Specifications

| HTTP Method | Route | Request Schema | Response Schema | Description |
|---|---|---|---|---|
| `GET` | `/production/health` | None | `HealthResponse` | Verifies service health, active capabilities, and error boundary status. |
| `GET` | `/production/metrics` | None | `MetricsResponse` | Returns canonical SHA-256 state hash proof and active review metrics. |
| `POST` | `/production/biotech/audit` | `BiotechAuditRequest` | `EvaluationRubric` | Executes full deterministic audit on candidate payloads. |
| `POST` | `/production/biotech/evaluate` | `BiotechEvaluationRequest` | `EvaluationRubric` | Rule evaluation across candidate streams. |
| `POST` | `/production/biotech/review` | `ReviewPacketContract` | `CandidateReviewRecord` | Starts candidate review and assigns initial decision state. |
| `POST` | `/production/biotech/disagreement` | `DisagreementRecordRequest` | `CandidateReviewRecord` | Records Section 16 independent audit disagreement. |
| `POST` | `/production/biotech/extract` | `EntityExtractionRequest` | `LLMVerificationResponse` | Resilient semantic extraction with deterministic fallback. |

---

## 4. Git Diff Summary

```text
A  api/__init__.py
A  api/production.py
A  evaluation_engine/__init__.py
A  evaluation_engine/rule_engine.py
A  integrations/__init__.py
A  integrations/local_llm_client.py
A  security/__init__.py
A  security/middleware.py
A  task_selector/__init__.py
A  task_selector/review_orchestrator.py
A  tests/__init__.py
A  tests/conftest.py
A  tests/integration/__init__.py
A  tests/integration/test_deterministic_execution.py
A  tests/integration/test_production_api.py
A  tests/unit/__init__.py
A  tests/unit/test_local_llm_client.py
A  tests/unit/test_review_orchestrator.py
A  tests/unit/test_rule_engine.py
A  tests/unit/test_security_middleware.py
A  pytest.ini
A  requirements.txt
A  REVIEW_PACKET.md
A  CODE_PACKET.md
M  README.md
```
