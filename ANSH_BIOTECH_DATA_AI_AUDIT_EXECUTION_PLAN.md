# BIOTECH — ANSH (AI/ML + DATA AUDIT) EXECUTION PLAN

**Role:** ANSH — AI/ML + Data Audit Lead  
**Audit Partner:** Pratik Bhuvad (Analytical Correctness & Reproducibility) & Aman Pal (Pipeline Failure & Stress Testing)  
**Coordination Leads:** Raj (Convergence Lead), Karan (Technical Lead), Harsha (Review Lead)  
**Execution Window:** 3-Day Cycle (Parallel to Test 3 candidate submissions)  
**Status:** WORKING / EXECUTION READY  
**Primary Mandate:** Independently audit data structures, deterministic processing, AI/ML claims, data quality, validation, reproducibility, and evidence pipelines across the 4 candidate streams and core Biotech repositories.  
**Guiding Question:** *“Is the data and computational behaviour trustworthy and reproducible?”*

---

## 1. Role Scope & Operational Boundaries

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  ANSH AUDIT MANDATE                                     │
├───────────────────────────────┬─────────────────────────────────────────────────────────┤
│ Core Responsibility           │ AI/ML Validation, Data Structures, Pipeline Integrity    │
├───────────────────────────────┼─────────────────────────────────────────────────────────┤
│ Verification Hierarchy        │ DOCUMENTED ──► IMPLEMENTED ──► EXECUTABLE ──►           │
│                               │ TESTED ──► REPRODUCIBLE ──► INTEGRABLE                  │
├───────────────────────────────┼─────────────────────────────────────────────────────────┤
│ First Principles              │ "No blame games. Only product delivery."                │
│                               │ Audit the product, evidence, schemas, and determinism.  │
├───────────────────────────────┼─────────────────────────────────────────────────────────┤
│ Non-Negotiable Boundary       │ We validate software and evidence management only.      │
│                               │ NO automated medical, clinical, regulatory, or drug     │
│                               │ approval decision engines. Human review must be preserved│
└───────────────────────────────┴─────────────────────────────────────────────────────────┘
```

---

## 2. The 4 Audited Candidate Streams & Scope

Ansh independently audits the data and computational layer of each candidate stream:

| Candidate | Stream / Capability | Ansh's Specific Audit Focus |
|---|---|---|
| **Sara** | Formulation & Stability Evidence Intelligence | Shelf-life/kinetic math determinism; excipient-API compatibility schemas; forced degradation data structures; preservation of assay raw units. |
| **Shravani** | Drug Safety Evidence Integration | OpenFDA/FAERS signal detection formulas (PRR, ROR); multi-drug attribution logic; MedDRA term normalization; adverse event evidence schemas. |
| **Shamit** | TB Drug-Discovery Candidate Intelligence | Molecular structure representations (SMILES/InChI validity); target binding assay data structures (IC50, Ki, MIC against M. tuberculosis); candidate ranking determinism. |
| **Shyamal** | Biosimilarity & Preclinical Evidence QC | Analytical similarity metrics; Tier 1/2/3 equivalence testing logic; preclinical animal study QC schemas; outlier and duplicate detection. |
| **Baseline Core** | Repo 1 (Pharmacovigilance) & Repo 2 (MHEALTH) | Sarvesh's OpenFDA pipeline v1 and MHEALTH biometric telemetry service (biometric signal ranges, FHIR R4 export, SQLite persistence). |

---

## 3. 3-Day Phased Execution Matrix

```
       DAY 1                          DAY 2                          DAY 3
┌─────────────────────┐        ┌─────────────────────┐        ┌─────────────────────┐
│ Discover & Audit    │        │ Prepare Integration │        │ Final Convergence   │
├─────────────────────┤        ├─────────────────────┤        ├─────────────────────┤
│ • Map entry points  │        │ • Reproduce tests   │        │ • Audit Test 3 drops│
│ • Challenge AI/ML   │  ───►  │ • Inject failures   │  ───►  │ • Independent audit│
│ • Validate schemas  │        │ • Trace provenance  │        │ • Decision states   │
│ • Audit determinism │        │ • Verify synthetic  │        │ • Evidence sign-off │
└─────────────────────┘        └─────────────────────┘        └─────────────────────┘
```

### Day 1: Discovery & Independent Technical Audit
- **Step 1.1 — Inspect Real Assets vs Claims:**
  - Audit entry points, schemas, inputs, processing logic, and outputs for all 4 streams.
  - Challenge "AI/ML Claims": Verify if true neural networks / statistical models exist or if they are deterministic string/rule engines.
- **Step 1.2 — Schema & Provenance Audit:**
  - Audit field completeness, type strictness, missing value handling, and unique constraints.
  - Check provenance: source URI, accession numbers, timestamps, transformation run IDs.
- **Step 1.3 — Baseline Core Inspection:**
  - Re-verify Sarvesh's Repo 1 (Pharmacovigilance packaging and multi-drug attribution).
  - Re-verify MHEALTH Repo 2 (FastAPI lifespan, HTTPX/Starlette compatibility, enum cases).

### Day 2: Failure Testing, Reproducibility & Cross-Capability Audit
- **Step 2.1 — Failure Injection Testing (The 7 Mandatory Scenarios):**
  1. Valid baseline input
  2. Missing required fields (e.g., null drug name, missing SMILES)
  3. Invalid/out-of-bounds values (e.g., negative concentration, malformed coordinates)
  4. Exact duplicate payloads (idempotency check)
  5. Conflicting evidence records (must retain both records as `CONFLICT`, never average)
  6. Empty datasets / zero-byte files
  7. Malformed input (syntax corruption, invalid JSON/CSV)
- **Step 2.2 — Synthetic Data Isolation Check:**
  - Verify that synthetic/test data has explicit `is_synthetic=True` or `TEST_FIXTURE` metadata.
  - Ensure synthetic data cannot commingle with real FAERS or clinical observations.
- **Step 2.3 — Cross-Capability Redundancy & Canonical Boundaries:**
  - Compare evidence schemas across Sara, Shravani, Shamit, and Shyamal.
  - Identify reusable Biotech data layers (Canonical Evidence Schema, Provenance Ledger).

### Day 3: Convergence, Candidate Verification & Final Sign-Off
- **Step 3.1 — Candidate Submission Audit (Test 3):**
  - Run independent data audit on incoming candidate pull requests.
  - Apply the **Independent Audit Rule**: If Ansh disagrees with Raj/Karan/Harsha, record:
    ```text
    OBSERVATION: ...
    EVIDENCE: ...
    DIFFERING INTERPRETATION: ...
    REQUIRED VERIFICATION: ...
    ```
- **Step 3.2 — Decision States Governance:**
  - Assign strictly one of: `APPROVED`, `APPROVED WITH FIXES`, `REVISION REQUIRED`, `REJECTED`.
- **Step 3.3 — Final Evidence Packet Compilation:**
  - Compile `review_packet.md`, runtime logs, and verification proof for handover.

---

## 4. Ansh's Core Deliverables Register

| Deliverable File | Purpose | Day Due | Status |
|---|---|---|---|
| `ANSH_BIOTECH_DATA_AI_AUDIT_EXECUTION_PLAN.md` | Master operational strategy for Ansh | Day 1 | **COMPLETED** |
| `PRATIK_AUDIT_VS_ANSH_AUDIT_COMPARISON.md` | In-depth comparison between Pratik's audit and Ansh's Biotech audit | Day 1 | **COMPLETED** |
| `ANSH_BIOTECH_DATA_AI_AUDIT_REPORT.md` | Deep-dive technical findings on AI/ML, data schemas, determinism, and boundaries | Day 1-2 | **COMPLETED** |
| `BIOTECH_DATA_INTEGRITY_CHECKLIST.md` | Operational test matrix & failure injection protocols | Day 2 | **COMPLETED** |
