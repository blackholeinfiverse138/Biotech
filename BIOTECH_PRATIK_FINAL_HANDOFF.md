# BIOTECH — PRATIK BHUVAD

## Final AI/ML + Data Audit Handoff
**Auditor:** Pratik Bhuvad  
**Role:** Independent AI/ML + Data Auditor  
**Recipients:** Raj, Karan, Harsha, Ansh, Aman (Engineering, ML & Data Integration Team)  
**Date:** 2026-09-30  
**Phase:** Phase 3 — Final Audit Packaging & Registers  
**Authoritative Reference:** [BIOTECH_PRATIK_INDEPENDENT_AUDIT.md](file:///c:/Pratik_Bhuwad/Biotech/BIOTECH_PRATIK_INDEPENDENT_AUDIT.md)

---

### 1. Audit Objective

The objective of this independent audit is to evaluate the technical reproducibility, data integrity, pipeline execution, and analytical validity of the two core Biotech repositories. The guiding investigative question across all phases is:

> **Can another developer reproduce the same result from the supplied inputs?**

All evaluations strictly follow the verification chain:
```text
DOCUMENTED ──► IMPLEMENTED ──► EXECUTABLE ──► TESTED ──► REPRODUCIBLE ──► INTEGRABLE
```

---

### 2. Repositories Audited

1. **Repository 1 (`Live-Pharmacovigilance-Evidence-And-Drug-Safety-Intelligence-Pipeline-v1-AI-Biotech-Core-Task-1-main`):**
   - **Canonical Directory:** [`Live-Pharmacovigilance-Evidence-And-Drug-Safety-Intelligence-Pipeline-v1-AI-Biotech-Core-Task-1-main`](file:///c:/Pratik_Bhuwad/Biotech/Live-Pharmacovigilance-Evidence-And-Drug-Safety-Intelligence-Pipeline-v1-AI-Biotech-Core-Task-1-main)
   - **Functional Role:** Pharmacovigilance Core Pipeline v1
   - **Documented Author:** Sarvesh Patil
   - **Scope:** Ingestion of OpenFDA / FAERS adverse event reports, entity normalization, alias matching, and evidence store persistence.

2. **Repository 2 (`bhiv-MHEALTH-Production-main`):**
   - **Canonical Directory:** [`bhiv-MHEALTH-Production-main`](file:///c:/Pratik_Bhuwad/Biotech/bhiv-MHEALTH-Production-main)
   - **Functional Role:** BHIV MHEALTH Production Runtime Task 4
   - **Documented Owner:** MHEALTH Task 4 Engineering Team
   - **Scope:** FastAPI REST microservice ingesting CSV/JSON patient biometric telemetry, rule-based classification against threshold bounds, SQLite/PostgreSQL persistence, dataset provenance tracking, and HL7 FHIR R4 Observation export.

---

### 3. AI/ML Verification

```text
No ML model was identified in either audited repository.
```

- **Repository 1 (`Live-Pharmacovigilance-Evidence-And-Drug-Safety-Intelligence-Pipeline-v1-AI-Biotech-Core-Task-1-main`):** Advertised in top-level documentation with AI/intelligence terminology, but the implementation relies entirely on deterministic string normalization (`normalize_record()`) and hardcoded dictionary alias lookups (`resolve_entity()`). No neural network, statistical classifier, weights file, embeddings, or training loop exists.
- **Repository 2 (`bhiv-MHEALTH-Production-main`):** Telemetry classification (`classify_signal()`) is executed via deterministic range comparison (`if value < lower: WARNING elif value > critical: CRITICAL`) loaded from a static JSON configuration (`configs/thresholds.json`). No ML models, feature stores, or model registry artifacts exist.
- **Auditor Conclusion:** Both repositories are deterministic software rule engines. No negative defect is assigned for the absence of ML models, but the team must recognize that no ML convergence or model-serving infrastructure is currently present.

---

### 4. Verified Findings

The following 10 findings have been independently verified through executable diagnostic scripts, failure tests, and source inspection.

#### Repository 1: `Live-Pharmacovigilance-Evidence-And-Drug-Safety-Intelligence-Pipeline-v1-AI-Biotech-Core-Task-1-main` (Pharmacovigilance)

1. **AUDIT-PV-001 — Missing `src` Package Hierarchy & Broken Imports**
   - **Repository:** Repo 1 (Pharmacovigilance)
   - **Observation:** Source and test files are placed flat in the repository root, but internal imports expect a `src.*` package namespace (e.g., `from src.openfda_connector import ...`). Furthermore, `pytest.ini` targets `tests/`, which does not exist.
   - **Evidence:** Executing `pytest -q` fails on collection with `ModuleNotFoundError: No module named 'src'`. Executing `python app.py` crashes at line 16 with the same error.
   - **Impact:** Any engineer cloning the repository cannot execute the CLI or test suite out-of-the-box.
   - **Status:** **CONFIRMED DEFECT / PACKAGING BLOCKER.**

2. **AUDIT-PV-002 — Multi-Drug Regimen Entity Resolution Misattribution**
   - **Repository:** Repo 1 (Pharmacovigilance)
   - **Observation:** When a FAERS report contains multiple concomitant medications (e.g., `[ASPIRIN, IBUPROFEN]`), `normalize_record()` unconditionally selects `drugs[0]`, ignoring the query drug.
   - **Evidence:** Querying for `"IBUPROFEN"` against a multi-drug record containing `ASPIRIN` at index 0 results in an `EvidenceRecord` where `drug_name="ASPIRIN"` and `confidence=0.9`. Verified deterministically in audit test harness.
   - **Impact:** Systematic attribution error in multi-drug therapy adverse event analysis.
   - **Status:** **CONFIRMED ANALYTICAL DEFECT.**

3. **AUDIT-PV-003 — Permissive Clinical Evidence Schema**
   - **Repository:** Repo 1 (Pharmacovigilance)
   - **Observation:** `evidence_schema.py:validate_evidence()` allows records with `drug_name=None`, `drug_name=""`, `adverse_event=None`, or `adverse_event=""` to pass validation as valid.
   - **Evidence:** Executing validation against records with `None` or empty strings returns `is_valid: True` with empty error lists.
   - **Impact:** Unanchored adverse event records can enter the persistence store without entity attribution.
   - **Status:** **CONFIRMED SCHEMA / VALIDATION GAP.**

4. **AUDIT-PV-004 — OpenFDA Query Syntax Sensitivity to Complex Input**
   - **Repository:** Repo 1 (Pharmacovigilance)
   - **Observation:** `openfda_connector.py` constructs queries using strict quotes: `patient.drug.medicinalproduct:"<name>"`. Certain complex strings with punctuation can cause upstream HTTP 500 query parsing errors from OpenFDA.
   - **Evidence:** Verified query construction syntax in `openfda_connector.py:L18-L23`.
   - **Impact:** Live data acquisition failure on complex chemical names or multi-word formulations.
   - **Status:** **CONFIRMED INPUT HANDLING RISK** (External Dependency Sensitivity).

---

#### Repository 2: `bhiv-MHEALTH-Production-main` (MHEALTH)

5. **AUDIT-MH-001 — Starlette TestClient / Modern HTTPX Compatibility Failure**
   - **Repository:** Repo 2 (MHEALTH)
   - **Observation:** `requirements.txt` leaves `httpx` unpinned. Starlette 0.27's `TestClient` passes the deprecated `app` keyword argument to `httpx.Client`, which was removed in `httpx >= 0.28.0`.
   - **Evidence:** Executing `pytest` directly in an environment with `httpx 0.28.1` causes all 39 tests to fail immediately with `TypeError: Client.__init__() got an unexpected keyword argument 'app'`.
   - **Impact:** Automated CI/CD test pipelines fail completely on fresh dependency installation.
   - **Status:** **CONFIRMED DEPENDENCY COMPATIBILITY GAP.**

6. **AUDIT-MH-002 — Windows SQLite File Handle Locking During Test Cleanup**
   - **Repository:** Repo 2 (MHEALTH)
   - **Observation:** `app/database/db.py` creates SQLite connection handles that are not explicitly closed before pytest fixtures attempt to delete temporary database files.
   - **Evidence:** Test execution on Windows terminates with `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process` during fixture cleanup.
   - **Impact:** Test suite crashes during teardown on Windows developer workstations.
   - **Status:** **CONFIRMED RESOURCE MANAGEMENT / PLATFORM GAP.**

7. **AUDIT-MH-003 — Ingestion Lacks Deduplication Mechanism**
   - **Repository:** Repo 2 (MHEALTH)
   - **Observation:** Re-uploading an identical CSV file or re-submitting identical telemetry measurements creates new dataset IDs and fresh random UUIDs for all rows without deduplication.
   - **Evidence:** Submitting duplicate telemetry payloads produces duplicate database rows with distinct signal UUIDs.
   - **Impact:** Repeat ingestion causes silent telemetry inflation and duplicate records in database and FHIR exports.
   - **Status:** **DATA INTEGRITY RISK** (Explicitly refined: Not a documented contract violation, as cross-upload deduplication is not stated as a formal requirement in repository docs).

8. **AUDIT-MH-004 — Synthetic Telemetry Lacks Provenance Metadata Flag**
   - **Repository:** Repo 2 (MHEALTH)
   - **Observation:** Synthetic test datasets (e.g., `subj-01`, `subj-02` in `test-signals.csv`) are ingested, stored, and exported as HL7 FHIR R4 Observations without an explicit `is_synthetic` flag or metadata marker.
   - **Evidence:** Ingestion schema and database schema omit synthetic indicators; exported FHIR Observations are indistinguishable from real patient observations.
   - **Impact:** Risk of synthetic test signals commingling with real patient telemetry in downstream clinical data warehouses.
   - **Status:** **DATA PROVENANCE / INTEGRATION RISK** (Software/data observation only; no clinical conclusions).

9. **AUDIT-MH-005 — Case Sensitivity Discrepancy Between CSV and JSON Ingestion**
   - **Repository:** Repo 2 (MHEALTH)
   - **Observation:** CSV ingestion converts enum fields to lowercase, whereas the direct JSON endpoint (`/signal/classify`) enforces strict uppercase Pydantic enum validation (`SignalType.HEART_RATE`, `DeviceSource.WEARABLE`).
   - **Evidence:** Submitting `{"signal_type": "heart_rate"}` to `/signal/classify` returns HTTP 422 Unprocessable Entity.
   - **Impact:** API consumers face inconsistent normalization contracts across endpoints.
   - **Status:** **API CONTRACT / INPUT NORMALIZATION GAP.**

10. **AUDIT-MH-006 — Database Initialization Coupled to FastAPI Lifespan**
    - **Repository:** Repo 2 (MHEALTH)
    - **Observation:** DDL schema initialization (`init_db()`) is exclusively wired to the FastAPI application `lifespan` context manager.
    - **Evidence:** Importing and invoking database functions from standalone scripts or CLI tasks without entering the lifespan raises `sqlite3.OperationalError: no such table: signals`.
    - **Impact:** Out-of-band batch processing, standalone migrations, and direct module testing require explicit lifespan emulation.
    - **Status:** **EXECUTION / LIFECYCLE DEPENDENCY.**

---

### 5. Reproducibility Status

| Repository | Out-of-the-Box Reproducibility | Workaround Reproducibility | Execution Evidence |
|---|---|---|---|
| **Repo 1 (Pharmacovigilance)** | **BLOCKED**<br>(`ModuleNotFoundError: No module named 'src'`) | **VERIFIED PASSING (100%)**<br>(47/47 unit tests pass in 0.14s) | Aliased `sys.modules['src']` to repository root in external wrapper; zero source files modified. |
| **Repo 2 (MHEALTH)** | **BLOCKED**<br>(`TypeError: unexpected keyword 'app'` & `[WinError 32]`) | **VERIFIED PASSING (100%)**<br>(39/39 integration tests pass in 3.29s) | Subclassed Starlette `TestClient` in external diagnostic runner; isolated SQLite handles; zero source files modified. |

---

### 6. Gap Register Summary

The comprehensive team gap catalog is maintained in [BIOTECH_GAP_REGISTER.md](file:///c:/Pratik_Bhuwad/Biotech/BIOTECH_GAP_REGISTER.md). It outlines:
- 10 detailed gap specifications (`GAP-PV-001` through `GAP-PV-004`, `GAP-MH-001` through `GAP-MH-006`).
- Contractual compliance classification (Contract Violations vs Architectural/Data Risks).
- Documented owners (`Sarvesh Patil` for Repo 1; `MHEALTH Task 4 Team` for Repo 2).
- Concrete technical remedies and required verification criteria.

---

### 7. Dependency Register Summary

The authoritative runtime, testing, and environmental dependency catalog is maintained in [BIOTECH_DEPENDENCY_REGISTER.md](file:///c:/Pratik_Bhuwad/Biotech/BIOTECH_DEPENDENCY_REGISTER.md). Key findings include:
- **DEP-PV-001:** Uncontrolled live dependency on the public US FDA OpenFDA REST API (`https://api.fda.gov`).
- **DEP-PV-002:** Structural dependency on a missing `src/` directory layout.
- **DEP-PV-003:** Unpinned `requests` dependency without a `requirements.txt` manifest.
- **DEP-MH-001:** Version conflict between Starlette 0.27 and unpinned modern `httpx >= 0.28.0`.
- **DEP-MH-002:** Windows platform sensitivity to unclosed SQLite file handles during fixture teardown.
- **DEP-MH-007:** Dependency on static clinical terminology standards (`LOINC 8867-4`, `UCUM`).

---

### 8. Convergence Register Summary

The cross-repository architectural evaluation is documented in [BIOTECH_CONVERGENCE_REGISTER.md](file:///c:/Pratik_Bhuwad/Biotech/BIOTECH_CONVERGENCE_REGISTER.md). Key takeaways:
- Evaluated across 15 standard dimensions: 9 Incompatible, 4 Partially Compatible, 1 Not Applicable (AI/ML), 1 Unknown.
- **No Direct Contract Identified:** No shared schema, API interface, or data pipeline currently connects the two systems.
- **Strict Boundary Preserved:** The audit explicitly refrains from prescribing code mergers. Every potential integration is framed as:
  > *Potential convergence point identified. Requires team-level contract decision before implementation.*

---

### 9. Open Team Decisions

The following 10 technical decisions require discussion and formal consensus among Raj, Karan, Harsha, Ansh, Aman, and the engineering team:

1. **Repository 1 Packaging Layout:**
   - *Question for Team:* Should Repository 1 be refactored into a standard Python layout with a top-level `src/` directory, or should internal imports be altered to root-relative imports?
2. **Multi-Drug Attribution Contract:**
   - *Question for Team:* In multi-drug FAERS safety reports, what is the required entity attribution rule? Should the pipeline search for the requested query drug in `patient.drug`, attribute all concomitant drugs, or report co-reported drug combinations?
3. **Clinical Schema Strictness:**
   - *Question for Team:* Should `drug_name` and `adverse_event` be strictly required non-empty strings in `evidence_schema.py`, rejecting incomplete records, or is permissive storage intentionally allowed?
4. **MHEALTH Telemetry Deduplication Policy:**
   - *Question for Team:* Is cross-upload telemetry deduplication required for production? If so, what natural key combination (e.g., `subject_id + recorded_at + signal_type + payload`) should govern idempotency?
5. **Synthetic Data Provenance Representation:**
   - *Question for Team:* Should synthetic test telemetry include an explicit `is_synthetic: bool` metadata flag across database schemas and FHIR R4 Observation exports?
6. **Dependency Version Pinning & Manifest Standardization:**
   - *Question for Team:* What exact versions of `fastapi`, `starlette`, `httpx`, and `requests` should be locked in `requirements.txt` across both repositories to guarantee deterministic builds?
7. **Supported CI/CD & Platform Environments:**
   - *Question for Team:* What operating systems (Linux, macOS, Windows) and Python versions (3.10, 3.11, 3.12) are officially supported for automated test execution?
8. **Enum Normalization Uniformity:**
   - *Question for Team:* Should CSV and JSON ingestion endpoints share the same input normalization contract (e.g., accepting case-insensitive enums across all entry points)?
9. **Database Initialization & Lifecycle Architecture:**
   - *Question for Team:* Should database schema creation (`init_db()`) be decoupled from the FastAPI `lifespan` handler to facilitate standalone CLI scripts, background workers, and testing?
10. **External AI/ML Model Dependencies:**
    - *Question for Team:* Are there external machine learning models, model registries, or embedding endpoints intended to integrate with these repositories that are not present in the current source trees?

---

### 10. Implementation Boundary

In accordance with strict independent audit protocols:

```text
APPLICATION SOURCE FILES MODIFIED: NO
APPLICATION TEST FILES MODIFIED: NO
ML MODEL CREATED: NO
REPOSITORIES MERGED: NO
```

All investigations, test runs, and verifications were performed using non-invasive external diagnostic scripts located outside the application repositories. The original codebase remains untouched.

---

### 11. Final Audit State

Based on the verified evidence chain across both repositories:

```text
DOCUMENTED:     PARTIAL   (Documentation exists but contains inaccuracies regarding packaging, tests, and deduplication)
IMPLEMENTED:    YES       (Core pipeline logic and API services are implemented)
EXECUTABLE:     YES       (Both systems execute with verified diagnostic wrappers)
TESTED:         YES       (Repo 1: 47/47 passing; Repo 2: 39/39 passing via wrappers)
REPRODUCIBLE:   BLOCKED   (Out-of-the-box reproduction fails due to missing src layout and Starlette/HTTPX conflict)
INTEGRABLE:     BLOCKED   (No shared contracts, schemas, or network interfaces currently connect the systems)
OVERALL STATE:  BLOCKED OUT-OF-BOX / VERIFIED PASSING WITH WRAPPER
```
