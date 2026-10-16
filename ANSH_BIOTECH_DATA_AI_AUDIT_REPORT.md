# BIOTECH — ANSH INDEPENDENT DATA & AI/ML AUDIT REPORT

**Auditor:** ANSH  
**Role:** AI/ML + Data Audit Lead  
**Audit Partner:** Pratik Bhuvad (Analytical Integrity), Aman Pal (Pipeline Failure Testing)  
**Task Scope:** 4 Candidate Streams (Sara, Shravani, Shamit, Shyamal) + Core Repositories (Sarvesh Repo 1, MHEALTH Repo 2)  
**Status:** DAY 1-2 COMPLETED / CONVERGENCE PREPARED  
**Core Investigative Question:** *“Is the data and computational behaviour trustworthy and reproducible?”*  
**Operational Rule:** Zero codebase mutation. Verification via non-invasive testing and independent validation.

---

## 1. Executive Summary & Verification Matrix

Across the audited repositories and candidate capability specifications, this independent audit evaluated the pipeline against the six-stage verification ladder:
`DOCUMENTED ──► IMPLEMENTED ──► EXECUTABLE ──► TESTED ──► REPRODUCIBLE ──► INTEGRABLE`

```
┌─────────────────────────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ CAPABILITY / STREAM             │ DOCUMENTED   │ IMPLEMENTED  │ EXECUTABLE   │ TESTED       │ REPRODUCIBLE │ INTEGRATION  │
├─────────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 1. Repo 1: Pharmacovigilance    │ YES          │ YES          │ YES (wrapper)│ YES (47/47)  │ BLOCKED (oob)│ READY W/ FIX │
│    Core v1 (Sarvesh Patil)      │              │              │              │              │ PASS (wrap)  │              │
├─────────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 2. Repo 2: MHEALTH Production   │ YES          │ YES          │ YES (wrapper)│ YES (39/39)  │ BLOCKED (oob)│ READY W/ FIX │
│    Task 4 (Biometric Telemetry) │              │              │              │              │ PASS (wrap)  │              │
├─────────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 3. Sara: Formulation & Stability│ YES          │ IN PROGRESS  │ PENDING      │ PENDING      │ PENDING      │ BLOCKED ON   │
│    Evidence Intelligence        │ (Test 3)     │ (Candidate)  │ TEST 3 DROP  │ TEST 3 DROP  │ TEST 3 DROP  │ TEST 3 DROP  │
├─────────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 4. Shravani: Drug Safety        │ YES          │ IN PROGRESS  │ PENDING      │ PENDING      │ PENDING      │ BLOCKED ON   │
│    Evidence Integration         │ (Test 3)     │ (Candidate)  │ TEST 3 DROP  │ TEST 3 DROP  │ TEST 3 DROP  │ TEST 3 DROP  │
├─────────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 5. Shamit: TB Drug-Discovery    │ YES          │ IN PROGRESS  │ PENDING      │ PENDING      │ PENDING      │ BLOCKED ON   │
│    Candidate Intelligence       │ (Test 3)     │ (Candidate)  │ TEST 3 DROP  │ TEST 3 DROP  │ TEST 3 DROP  │ TEST 3 DROP  │
├─────────────────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 6. Shyamal: Biosimilarity &     │ YES          │ IN PROGRESS  │ PENDING      │ PENDING      │ PENDING      │ BLOCKED ON   │
│    Preclinical Evidence QC      │ (Test 3)     │ (Candidate)  │ TEST 3 DROP  │ TEST 3 DROP  │ TEST 3 DROP  │ TEST 3 DROP  │
└─────────────────────────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 2. Section 9 Audit: Data & AI/ML Integrity Findings

### A. AI/ML Ground Reality Verification
- **Finding:** Neither Repo 1 nor Repo 2 implements artificial intelligence or machine learning models.
- **Evidence:**
  - Repo 1 advertises "AI-Biotech-Core", but utilizes string lowercase normalization and a static Python dictionary lookup (`resolve_entity()`).
  - Repo 2 classifies biometric signals using a static JSON configuration (`configs/thresholds.json`) with scalar comparison operators (`if value < lower: WARNING`).
- **Ansh's Audit Assessment:** Reclassify both systems as **Deterministic Rule & Ingestion Engines**. This eliminates technical debt and prevents downstream engineers from attempting to configure model registries or GPU runtimes.

### B. Input Integrity
1. **Missing Data Vulnerability (`AUDIT-PV-003`):**
   - In `evidence_schema.py:validate_evidence()`, empty or null fields (`drug_name=None`, `adverse_event=""`) are accepted as valid records (`is_valid: True`).
   - *Required Fix:* Implement mandatory non-empty string validation at the schema boundary.
2. **Contract Case Discrepancy (`AUDIT-MH-005`):**
   - Telemetry CSV ingestion converts fields to lowercase, while JSON endpoints require strict uppercase Pydantic enums (`SignalType.HEART_RATE`).
   - *Impact:* Submitting lowercase values to the REST API causes HTTP 422 validation errors.
3. **Punctuation Sensitivity in External Queries (`AUDIT-PV-004`):**
   - `openfda_connector.py` constructs literal quote queries `patient.drug.medicinalproduct:"<name>"`. Unsanitized drug names with chemical punctuation (e.g., dashes, commas, salts) cause OpenFDA upstream HTTP 500 parse failures.

### C. Processing Integrity & Determinism
1. **Multi-Drug Therapy Attribution Error (`AUDIT-PV-002`):**
   - In multi-drug FAERS safety reports, `normalize_record()` takes `drugs[0]` unconditionally.
   - *Demonstrated Failure:* Querying for `IBUPROFEN` against a report containing `[ASPIRIN, IBUPROFEN]` returns an evidence record for `ASPIRIN` with `confidence=0.9`.
   - *Ansh's Audit Directive:* Multi-drug records must be matched against the queried drug entity or structured as co-reported concomitant drug pairs.
2. **Absence of Cross-Upload Deduplication (`AUDIT-MH-003`):**
   - Re-uploading identical telemetry files mints new random UUIDs for all rows without idempotency checking.
   - *Impact:* Duplicate uploads inflate historical metrics and produce redundant FHIR observations.

### D. Synthetic Data Governance & Contamination Prevention
1. **Synthetic Telemetry Leakage into Standard FHIR R4 (`AUDIT-MH-004`):**
   - In MHEALTH, synthetic test records (`subj-01`, `subj-02`) are stored in SQLite and exported as standard HL7 FHIR R4 `Observation` resources.
   - *Failure:* No `is_synthetic` boolean or FHIR metadata extension tag exists.
   - *Risk:* Downstream clinical databases cannot distinguish test fixtures from genuine human vitals.
   - *Mandatory Rule:* All synthetic records must retain explicit `is_synthetic=True` metadata from ingestion through FHIR export.

### E. Output Integrity & Schema Usability
- Output schemas in both pipelines provide clean field names, but lack explicit units in certain summary views.
- MHEALTH adheres to `LOINC 8867-4` and `UCUM` standard clinical coding, which is a major positive for interoperability.

---

## 3. Section 8: Enforcement of Scientific & Regulatory Boundaries

```text
CRITICAL BOUNDARY ENFORCED:
---------------------------
SOFTWARE & EVIDENCE MANAGEMENT ONLY
NO MEDICAL DECISION ENGINE
NO CLINICAL ADJUDICATION
NO AUTONOMOUS FDA APPROVAL OR DRUG DISCOVERY RULING
```

1. **Preserving Human Review:**
   - Shravani's safety signal calculation (PRR / ROR) is a mathematical aggregation of reported events; it is **not** an adjudication that a drug causes an adverse event.
   - Sara's formulation stability models are kinetic estimations; they are **not** regulatory shelf-life certifications.
   - Shamit's TB candidate scoring is computational triage; it is **not** a clinical efficacy endorsement.
   - Shyamal's biosimilarity QC is statistical equivalence testing; it is **not** a regulatory biosimilar approval.
2. **Handling Scientific Conflict:**
   - Conflicting adverse event reports or conflicting assay results must **never** be averaged.
   - In accordance with the inherited principle (`RULE_DEDUP_CONFLICT`), both records must be stored and explicitly flagged as `CONFLICT` for expert human review.

---

## 4. Candidate Streams Audit Checklist (For Test 3 Drops)

When Sara, Shravani, Shamit, and Shyamal submit their Test 3 code packages, Ansh will execute the following verification checklist:

```
┌─────────────────────────────────┬─────────────────────────────────────────────────────────────┐
│ Candidate Stream                │ Ansh's Mandatory Verification Check                         │
├─────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ **Sara**                        │ • Are kinetic degradation formulas (Arrhenius) deterministic│
│ (Formulation & Stability)       │ • Are assay units preserved (pH, % degradation, temp °C)?   │
│                                 │ • How are conflicting stability tests under same RH handled?│
├─────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ **Shravani**                    │ • Does PRR/ROR calculation handle zero-division safely?     │
│ (Drug Safety Integration)       │ • Is multi-drug concomitant attribution fixed (no drugs[0])?│
│                                 │ • Are MedDRA terms validated against a canonical dictionary?│
├─────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ **Shamit**                      │ • Are SMILES strings validated via RDKit / standard parsers?│
│ (TB Drug Discovery)             │ • Are IC50 / MIC units explicitly labeled (nM, µM, µg/mL)?  │
│                                 │ • Is candidate ranking strictly deterministic on same seed? │
├─────────────────────────────────┼─────────────────────────────────────────────────────────────┤
│ **Shyamal**                     │ • Are statistical similarity intervals (Tier 1/2/3) tested? │
│ (Biosimilarity & QC)            │ • Are preclinical animal IDs validated against duplicates?  │
│                                 │ • Does outlier detection flag anomalies without dropping?   │
└─────────────────────────────────┴─────────────────────────────────────────────────────────────┘
```

---

## 5. Section 16: Independent Audit Disagreement Register

Under the Section 16 Independent Audit Rule, Ansh must record any independent technical disagreements with other leads (Raj, Karan, Harsha) using the standard format:

### Case 1: AI/ML Capability Labeling
- **OBSERVATION:** Documentation and team discussions refer to Repo 1 and Repo 2 as "AI Capabilities" requiring AI convergence and model registry integration.
- **EVIDENCE:** Comprehensive code inspection proves zero neural networks, zero ML dependencies, zero model weights, and zero statistical learning loops exist in either repository.
- **DIFFERING INTERPRETATION:** Raj/Karan view these as AI modules with missing weights; Ansh independently evaluates them as pure deterministic software rule engines.
- **REQUIRED VERIFICATION:** Remove AI/ML convergence blockers from Day 3 integration plans. Treat both repositories as deterministic microservices.

### Case 2: Ingestion Permissiveness vs Schema Enforcement
- **OBSERVATION:** Repo 1 permits records with empty `drug_name` and `adverse_event` to pass validation and enter storage.
- **EVIDENCE:** `test_evidence_schema.py` confirms `validate_evidence({"drug_name": "", "adverse_event": ""})` returns `is_valid: True`.
- **DIFFERING INTERPRETATION:** Harsha considers this acceptable for permissive ingestion; Ansh considers it a fatal data integrity defect that pollutes the evidence layer.
- **REQUIRED VERIFICATION:** Enforce non-empty string validation before records are permitted to persist.

---

## 6. Day 3 Readiness Verdict

```text
OVERALL AUDIT VERDICT: READY FOR DAY 3 CONVERGENCE (WITH SPECIFIED WRAPPERS & FIXES)
REPOSITORIES TESTED: 2 (86/86 TESTS PASSING VIA DIAGNOSTIC WRAPPERS)
CANDIDATE STREAMS PREPARED: 4 (VERIFICATION CHECKLISTS AND FAILURE TEST SUITES STAGED)
SCIENTIFIC BOUNDARIES PRESERVED: 100%
```
