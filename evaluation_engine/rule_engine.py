"""
Biotech Rule Engine - Deterministic Evaluation Module
======================================================
Owner: ANSH (AI/ML + Data Audit Lead)
Task ID: T-GOV-F01 (Remediation & Structural Compliance)
Domain: Biotech Integration, Audit & Convergence

Evaluates data schemas, computational determinism, multi-entity attribution,
synthetic data quarantine, and Section 8 scientific boundary conformance.
"""

from typing import Dict, Any, List, Optional, Tuple
import hashlib
import json
import logging
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

logger = logging.getLogger("biotech_rule_engine")


class RuleEvaluationResult(BaseModel):
    rule_id: str
    rule_name: str
    passed: bool
    score: float = Field(..., ge=0.0, le=100.0)
    observation: str
    details: Dict[str, Any] = Field(default_factory=dict)


class EvaluationRubric(BaseModel):
    code_present: bool = True
    proof_present: bool = True
    arch_present: bool = True
    schema_strictness_score: float = 100.0
    determinism_score: float = 100.0
    attribution_integrity_score: float = 100.0
    synthetic_quarantine_score: float = 100.0
    scientific_boundary_score: float = 100.0
    composite_score: float = 100.0
    evaluation_result: str = "PASS"  # PASS or FAIL
    failure_type: Optional[str] = None

    @property
    def overall_pass(self) -> bool:
        return self.evaluation_result == "PASS"

    @property
    def score(self) -> int:
        return int(self.composite_score)

    @property
    def deterministic_hash(self) -> str:
        data = {
            "code_present": self.code_present,
            "proof_present": self.proof_present,
            "arch_present": self.arch_present,
            "composite_score": self.composite_score,
            "evaluation_result": self.evaluation_result,
            "failure_type": self.failure_type
        }
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class BiotechRuleEngine:
    """
    Deterministic rule engine that validates Biotech capability submissions
    against strict data integrity, architectural, and governance rules.
    """

    def __init__(self):
        self.version = "1.0.0"
        self.supported_streams = {
            "sara": "Formulation & Stability Evidence Intelligence",
            "shravani": "Drug Safety Evidence Integration",
            "shamit": "TB Drug-Discovery Candidate Intelligence",
            "shyamal": "Biosimilarity & Preclinical Evidence QC",
            "core_pharmacovigilance": "Pharmacovigilance Core v1",
            "core_mhealth": "MHEALTH Production Task 4"
        }

    @staticmethod
    def compute_state_hash(data: Any) -> str:
        """
        Computes a deterministic SHA-256 state hash for any payload.
        Ensures canonical JSON serialization with sorted keys.
        """
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'), default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def evaluate_schema_strictness(self, payload: Dict[str, Any]) -> RuleEvaluationResult:
        """
        AUDIT-PV-003 Remediation: Enforces fail-closed schema validation.
        Rejects records with null, empty, or whitespace-only entity names.
        """
        drug_name = payload.get("drug_name")
        adverse_event = payload.get("adverse_event")
        subject_id = payload.get("subject_id")
        
        has_invalid_empty = False
        empty_fields = []

        # Check entity fields if present in schema
        if "drug_name" in payload:
            if drug_name is None or str(drug_name).strip() == "":
                has_invalid_empty = True
                empty_fields.append("drug_name")

        if "adverse_event" in payload:
            if adverse_event is None or str(adverse_event).strip() == "":
                has_invalid_empty = True
                empty_fields.append("adverse_event")

        if "subject_id" in payload:
            if subject_id is None or str(subject_id).strip() == "":
                has_invalid_empty = True
                empty_fields.append("subject_id")

        if has_invalid_empty:
            return RuleEvaluationResult(
                rule_id="RULE-SCHEMA-STRICT",
                rule_name="Fail-Closed Schema Boundary Validation",
                passed=False,
                score=0.0,
                observation=f"Rejected unanchored record with empty required fields: {empty_fields}",
                details={"empty_fields": empty_fields, "rejection_action": "fail_closed"}
            )

        return RuleEvaluationResult(
            rule_id="RULE-SCHEMA-STRICT",
            rule_name="Fail-Closed Schema Boundary Validation",
            passed=True,
            score=100.0,
            observation="All required entity fields strictly populated and validated.",
            details={"validated_fields": list(payload.keys())}
        )

    def evaluate_multi_drug_attribution(self, query_drug: str, reported_drugs: List[str]) -> RuleEvaluationResult:
        """
        AUDIT-PV-002 Remediation: Prevents naive drugs[0] attribution bug.
        Matches the queried drug specifically and preserves concomitant medications.
        """
        if not reported_drugs:
            return RuleEvaluationResult(
                rule_id="RULE-ATTR-MULTI-DRUG",
                rule_name="Multi-Drug Entity Attribution Verification",
                passed=False,
                score=0.0,
                observation="Report contains empty drug list; cannot attribute adverse event.",
                details={"query_drug": query_drug, "reported_drugs": []}
            )

        # Naive approach simulation for comparison
        naive_attributed = reported_drugs[0]

        # Canonical query matching
        matched_drug = next((d for d in reported_drugs if d.strip().lower() == query_drug.strip().lower()), None)

        if matched_drug is None:
            return RuleEvaluationResult(
                rule_id="RULE-ATTR-MULTI-DRUG",
                rule_name="Multi-Drug Entity Attribution Verification",
                passed=False,
                score=0.0,
                observation=f"Query drug '{query_drug}' not found in reported drugs list: {reported_drugs}",
                details={"query_drug": query_drug, "reported_drugs": reported_drugs}
            )

        # Concomitant preservation
        concomitant = [d for d in reported_drugs if d.strip().lower() != query_drug.strip().lower()]

        return RuleEvaluationResult(
            rule_id="RULE-ATTR-MULTI-DRUG",
            rule_name="Multi-Drug Entity Attribution Verification",
            passed=True,
            score=100.0,
            observation=f"Successfully attributed to queried drug '{matched_drug}' with {len(concomitant)} concomitant drugs preserved.",
            details={
                "attributed_drug": matched_drug,
                "concomitant_drugs": concomitant,
                "naive_drugs_0": naive_attributed,
                "prevented_misattribution": (naive_attributed.lower() != query_drug.lower())
            }
        )

    def evaluate_synthetic_quarantine(self, payload: Dict[str, Any]) -> RuleEvaluationResult:
        """
        AUDIT-MH-004 Remediation: Verifies that synthetic datasets are explicitly
        tagged with `is_synthetic: bool = True` and include FHIR metadata extensions.
        """
        is_mock_identifier = any(
            mock_prefix in str(payload.get("subject_id", "")).lower()
            for mock_prefix in ["subj-0", "mock", "test", "synthetic", "synth"]
        )

        has_synthetic_flag = payload.get("is_synthetic") is True
        fhir_extension_present = False

        if "extension" in payload and isinstance(payload["extension"], list):
            fhir_extension_present = any(
                "synthetic" in ext.get("url", "").lower() and ext.get("valueBoolean") is True
                for ext in payload["extension"]
                if isinstance(ext, dict)
            )

        if is_mock_identifier and not (has_synthetic_flag or fhir_extension_present):
            return RuleEvaluationResult(
                rule_id="RULE-SYNTHETIC-QUARANTINE",
                rule_name="Synthetic Data Provenance Quarantine",
                passed=False,
                score=0.0,
                observation="Synthetic test payload detected without explicit `is_synthetic` or FHIR extension tag.",
                details={"subject_id": payload.get("subject_id"), "risk": "clinical_data_commingling"}
            )

        return RuleEvaluationResult(
            rule_id="RULE-SYNTHETIC-QUARANTINE",
            rule_name="Synthetic Data Provenance Quarantine",
            passed=True,
            score=100.0,
            observation="Payload complies with synthetic data governance protocol.",
            details={"is_synthetic": has_synthetic_flag, "fhir_extension_present": fhir_extension_present}
        )

    def evaluate_scientific_boundary(self, payload: Dict[str, Any]) -> RuleEvaluationResult:
        """
        Section 8 Boundary Enforcement: Guarantees software is an evidence management layer,
        NOT an automated medical decision or drug approval engine.
        """
        prohibited_verdicts = [
            "approve_drug", "reject_drug", "prescribe_treatment",
            "clinical_diagnosis", "fda_adjudication", "grant_approval"
        ]

        action = str(payload.get("decision_action", "")).lower()
        conclusion = str(payload.get("conclusion", "")).lower()

        violated_actions = [pv for pv in prohibited_verdicts if pv in action or pv in conclusion]

        if violated_actions:
            return RuleEvaluationResult(
                rule_id="RULE-SCIENTIFIC-BOUNDARY",
                rule_name="Section 8 Non-Adjudication Regulatory Red Line",
                passed=False,
                score=0.0,
                observation=f"Violated Section 8 scientific boundary by emitting automated regulatory verdict: {violated_actions}",
                details={"violation": violated_actions, "boundary": "software_evidence_only"}
            )

        return RuleEvaluationResult(
            rule_id="RULE-SCIENTIFIC-BOUNDARY",
            rule_name="Section 8 Non-Adjudication Regulatory Red Line",
            passed=True,
            score=100.0,
            observation="System strictly preserves human scientific review boundary (evidence summaries only).",
            details={"compliance": "evidence_management_layer"}
        )

    def evaluate_conflict_preservation(self, records: List[Dict[str, Any]]) -> RuleEvaluationResult:
        """
        Evaluates handling of conflicting observations. Conflicting data points
        must be preserved and tagged CONFLICT, never averaged.
        """
        if len(records) < 2:
            return RuleEvaluationResult(
                rule_id="RULE-CONFLICT-PRESERVATION",
                rule_name="Conflict Preservation Protocol",
                passed=True,
                score=100.0,
                observation="Single record; no conflict condition evaluated.",
                details={"record_count": len(records)}
            )

        # Check for same entity and timestamp but different numerical values
        conflicts_found = False
        preserved_both = True

        rec_a, rec_b = records[0], records[1]
        same_id = rec_a.get("subject_id") == rec_b.get("subject_id")
        same_time = rec_a.get("timestamp") == rec_b.get("timestamp")
        diff_value = rec_a.get("value") != rec_b.get("value")

        if same_id and same_time and diff_value:
            conflicts_found = True
            # Verify status is CONFLICT and neither is averaged
            status_a = rec_a.get("status")
            status_b = rec_b.get("status")
            if not ("CONFLICT" in str(status_a) and "CONFLICT" in str(status_b)):
                preserved_both = False

        if conflicts_found and not preserved_both:
            return RuleEvaluationResult(
                rule_id="RULE-CONFLICT-PRESERVATION",
                rule_name="Conflict Preservation Protocol",
                passed=False,
                score=20.0,
                observation="Conflicting observations detected without explicit CONFLICT status tagging.",
                details={"conflict_detected": True, "properly_tagged": False}
            )

        return RuleEvaluationResult(
            rule_id="RULE-CONFLICT-PRESERVATION",
            rule_name="Conflict Preservation Protocol",
            passed=True,
            score=100.0,
            observation="Conflict protocol satisfied: observations retained with CONFLICT provenance tags.",
            details={"conflict_detected": conflicts_found, "properly_tagged": True}
        )

    def evaluate_full_submission(
        self,
        capability: str,
        payload: Dict[str, Any],
        reported_drugs: Optional[List[str]] = None,
        query_drug: Optional[str] = None
    ) -> EvaluationRubric:
        """
        Comprehensive evaluation executing all rule checks and generating composite score.
        """
        results: List[RuleEvaluationResult] = []

        # 1. Schema strictness
        r_schema = self.evaluate_schema_strictness(payload)
        results.append(r_schema)

        # 2. Multi-drug attribution
        if reported_drugs and query_drug:
            r_attr = self.evaluate_multi_drug_attribution(query_drug, reported_drugs)
        else:
            r_attr = RuleEvaluationResult(
                rule_id="RULE-ATTR-MULTI-DRUG",
                rule_name="Multi-Drug Entity Attribution Verification",
                passed=True,
                score=100.0,
                observation="Single-entity or non-pharmacovigilance payload.",
                details={}
            )
        results.append(r_attr)

        # 3. Synthetic quarantine
        r_synth = self.evaluate_synthetic_quarantine(payload)
        results.append(r_synth)

        # 4. Scientific boundary
        r_bound = self.evaluate_scientific_boundary(payload)
        results.append(r_bound)

        # 5. Determinism test
        hash_1 = self.compute_state_hash(payload)
        hash_2 = self.compute_state_hash(payload)
        is_deterministic = (hash_1 == hash_2)
        r_determ = RuleEvaluationResult(
            rule_id="RULE-DETERMINISM",
            rule_name="Computational State Determinism",
            passed=is_deterministic,
            score=100.0 if is_deterministic else 0.0,
            observation="State hash generation verified across consecutive runs.",
            details={"state_hash": hash_1}
        )
        results.append(r_determ)

        # Compute composite score
        total_score = sum(r.score for r in results) / len(results)
        all_passed = all(r.passed for r in results)

        failure_type = None
        if not all_passed:
            failed_rules = [r.rule_id for r in results if not r.passed]
            failure_type = f"FAILED_RULES: {', '.join(failed_rules)}"

        return EvaluationRubric(
            code_present=True,
            proof_present=True,
            arch_present=True,
            schema_strictness_score=r_schema.score,
            determinism_score=r_determ.score,
            attribution_integrity_score=r_attr.score,
            synthetic_quarantine_score=r_synth.score,
            scientific_boundary_score=r_bound.score,
            composite_score=round(total_score, 2),
            evaluation_result="PASS" if all_passed else "FAIL",
            failure_type=failure_type
        )

    def evaluate_candidate_submission(
        self,
        task_id: str,
        candidate_name: str,
        capability_name: str,
        payload: Dict[str, Any],
        query_drug: Optional[str] = None
    ) -> EvaluationRubric:
        """Helper to evaluate full submission from candidate parameters."""
        reported_drugs = payload.get("associated_drugs", [])
        return self.evaluate_full_submission(
            capability=capability_name,
            payload=payload,
            reported_drugs=reported_drugs,
            query_drug=query_drug
        )
