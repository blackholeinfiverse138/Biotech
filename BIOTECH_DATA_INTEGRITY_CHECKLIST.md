# BIOTECH — DATA & AI/ML INTEGRITY OPERATIONAL CHECKLIST

**Owner:** ANSH (AI/ML + Data Audit Lead)  
**Execution Context:** Day 2 & Day 3 Validation Suites  
**Target:** 4 Candidate Streams (Sara, Shravani, Shamit, Shyamal) + Core Services  

---

## 1. The 7 Mandatory Failure Injection Tests

For every endpoint and pipeline component, Ansh executes the following 7 test vectors:

```
┌────┬─────────────────────────────┬───────────────────────────────────────┬──────────────────────────────────────────┐
│ #  │ Test Vector                 │ Injected Input Payload                │ Expected Pipeline Behavior               │
├────┼─────────────────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
│ 1  │ Valid Baseline              │ Standard canonical record             │ Status: ACCEPTED / 200 OK; valid schema  │
├────┼─────────────────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
│ 2  │ Missing Required Field      │ Null/omitted entity name or ID        │ Explicit rejection (422 / ValidationError)│
├────┼─────────────────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
│ 3  │ Invalid / Out-of-Bounds     │ Negative dose; impossible pH (18.0)   │ Rejection with descriptive range error   │
├────┼─────────────────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
│ 4  │ Duplicate Record            │ Identical payload re-submitted        │ Idempotent response; no duplicate rows   │
├────┼─────────────────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
│ 5  │ Conflicting Record          │ Same entity & timestamp, diff value   │ Retain BOTH; flag as CONFLICT status     │
├────┼─────────────────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
│ 6  │ Empty Dataset               │ 0-byte file or empty list `[]`        │ Clean handling; 0 records; no crash/500  │
├────┼─────────────────────────────┼───────────────────────────────────────┼──────────────────────────────────────────┤
│ 7  │ Malformed Input             │ Broken JSON syntax; corrupted CSV     │ Catch parse error; return HTTP 400       │
└────┴─────────────────────────────┴───────────────────────────────────────┴──────────────────────────────────────────┘
```

---

## 2. Stream-Specific Data Verification Protocols

### Stream 1: Sara (Formulation & Stability Evidence Intelligence)
- [ ] **Kinetic Model Verification:** Check if degradation rate constants ($k$) and Arrhenius temperature extrapolations use deterministic mathematical libraries (`numpy`, `scipy`).
- [ ] **Physical Units Consistency:** Validate that stability matrices explicitly record temperature (°C/K), relative humidity (% RH), time intervals (hours/days/months), and concentration units (mg/mL).
- [ ] **Degradation Product Attribution:** Verify that impurity and degradant peaks are linked to specific stress conditions (photolytic, thermal, oxidative, hydrolytic) without orphan records.

### Stream 2: Shravani (Drug Safety Evidence Integration)
- [ ] **Multi-Drug Disproportionality Calculation:** Verify that Proportional Reporting Ratio (PRR) and Reporting Odds Ratio (ROR) formulas implement 0.5 Haldane continuity correction for zero-count cells to prevent `ZeroDivisionError`.
- [ ] **Entity Attribution Integrity:** Test against multi-ingredient medications. Guarantee that the pipeline does not fall back to `drugs[0]` naive selection.
- [ ] **MedDRA Hierarchy Mapping:** Verify that reported Adverse Events map to Preferred Terms (PT) and System Organ Classes (SOC) deterministically.

### Stream 3: Shamit (TB Drug-Discovery Candidate Intelligence)
- [ ] **Chemical Structure Sanitization:** Run SMILES and InChI strings through an RDKit/standard validator. Ensure invalid valences or broken rings are rejected at the input gate.
- [ ] **Assay Concentration Normalization:** Convert all bioactivity values (IC50, EC50, MIC against *M. tuberculosis* H37Rv) to standardized logarithmic scale ($\text{pIC}_{50} = -\log_{10}(\text{IC}_{50}\text{ in M})$).
- [ ] **Deterministic Candidate Ranking:** Verify that candidate scoring algorithms (combining potency, Lipinski Rule of 5 violations, and toxicity indicators) return identical sorted ranks across repeated runs.

### Stream 4: Shyamal (Biosimilarity & Preclinical Evidence QC)
- [ ] **Equivalence Testing Boundaries:** Confirm Tier 1 equivalence margins (e.g., $1.5 \times \text{SD}_R$) are calculated using unbiased variance estimators.
- [ ] **Preclinical Animal Subject IDs:** Guarantee animal cohort IDs, dose groups, and observation days maintain strict relational integrity with zero duplicates.
- [ ] **Outlier Handling Protocol:** Ensure outlier data points (e.g., in PK/PD clearance curves) are explicitly flagged with statistical criteria (Grubbs' test or Tukey IQR) rather than being silently excised.

---

## 3. Synthetic Data Quarantine Protocols

- [ ] Every synthetic test file must reside under a dedicated `tests/fixtures/synthetic/` or `data/mock/` directory.
- [ ] In-memory representations must require an immutable `is_synthetic: bool = True` attribute.
- [ ] In database tables (`evidence_records`, `signals`, `observations`), the column `is_synthetic` must be non-nullable with a default of `FALSE` for real ingestion, and explicitly set to `TRUE` during test loading.
- [ ] All FHIR R4 exports must include the custom extension:
  ```json
  {
    "url": "http://blackholeinfiverse.com/fhir/StructureDefinition/is-synthetic",
    "valueBoolean": true
  }
  ```
- [ ] Any test script that generates synthetic data must assert that synthetic data never leaks into the canonical persistent storage layer.
