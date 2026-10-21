"""
Unit Tests for BiotechRuleEngine
"""
import pytest
from evaluation_engine.rule_engine import BiotechRuleEngine, RuleEvaluationResult


def test_schema_strictness_valid(rule_engine):
    valid_payload = {
        "drug_name": "IBUPROFEN",
        "adverse_event": "Headache",
        "subject_id": "SUBJ-9921",
        "reported_at": "2026-10-01T10:00:00Z"
    }
    result = rule_engine.evaluate_schema_strictness(valid_payload)
    assert result.passed is True
    assert result.score == 100.0


def test_schema_strictness_fail_closed_empty_drug(rule_engine):
    # AUDIT-PV-003: empty drug_name must fail closed
    invalid_payload = {
        "drug_name": "",
        "adverse_event": "Headache",
        "subject_id": "SUBJ-9921"
    }
    result = rule_engine.evaluate_schema_strictness(invalid_payload)
    assert result.passed is False
    assert result.score == 0.0
    assert "drug_name" in result.details["empty_fields"]


def test_schema_strictness_fail_closed_null_adverse_event(rule_engine):
    invalid_payload = {
        "drug_name": "ASPIRIN",
        "adverse_event": None,
        "subject_id": "SUBJ-9921"
    }
    result = rule_engine.evaluate_schema_strictness(invalid_payload)
    assert result.passed is False
    assert result.score == 0.0
    assert "adverse_event" in result.details["empty_fields"]


def test_multi_drug_attribution_correct_match(rule_engine):
    # AUDIT-PV-002: Querying IBUPROFEN when reported is [ASPIRIN, IBUPROFEN, PARACETAMOL]
    reported = ["ASPIRIN", "IBUPROFEN", "PARACETAMOL"]
    result = rule_engine.evaluate_multi_drug_attribution(query_drug="IBUPROFEN", reported_drugs=reported)
    assert result.passed is True
    assert result.score == 100.0
    assert result.details["attributed_drug"] == "IBUPROFEN"
    assert "ASPIRIN" in result.details["concomitant_drugs"]
    assert result.details["prevented_misattribution"] is True


def test_multi_drug_attribution_not_found(rule_engine):
    reported = ["ASPIRIN", "PARACETAMOL"]
    result = rule_engine.evaluate_multi_drug_attribution(query_drug="METFORMIN", reported_drugs=reported)
    assert result.passed is False
    assert result.score == 0.0


def test_synthetic_quarantine_unflagged_rejected(rule_engine):
    # AUDIT-MH-004: mock subject without is_synthetic or FHIR tag must fail
    mock_payload = {
        "subject_id": "subj-01",
        "signal_type": "HEART_RATE",
        "value": 78.5
    }
    result = rule_engine.evaluate_synthetic_quarantine(mock_payload)
    assert result.passed is False
    assert result.score == 0.0


def test_synthetic_quarantine_flagged_accepted(rule_engine):
    mock_payload = {
        "subject_id": "subj-01",
        "signal_type": "HEART_RATE",
        "value": 78.5,
        "is_synthetic": True
    }
    result = rule_engine.evaluate_synthetic_quarantine(mock_payload)
    assert result.passed is True
    assert result.score == 100.0


def test_synthetic_quarantine_fhir_extension_accepted(rule_engine):
    fhir_payload = {
        "subject_id": "subj-02",
        "resourceType": "Observation",
        "extension": [{"url": "http://blackholeinfiverse.com/fhir/is-synthetic", "valueBoolean": True}]
    }
    result = rule_engine.evaluate_synthetic_quarantine(fhir_payload)
    assert result.passed is True
    assert result.score == 100.0


def test_scientific_boundary_prohibits_approval(rule_engine):
    # Section 8 Red Line
    violating_payload = {
        "drug_name": "RIFAMPICIN",
        "decision_action": "approve_drug_for_market",
        "conclusion": "Autonomous regulatory drug approval granted"
    }
    result = rule_engine.evaluate_scientific_boundary(violating_payload)
    assert result.passed is False
    assert result.score == 0.0


def test_scientific_boundary_allows_evidence_summary(rule_engine):
    evidence_payload = {
        "drug_name": "RIFAMPICIN",
        "decision_action": "generate_evidence_summary",
        "conclusion": "Calculated PRR=2.45 for human clinical review"
    }
    result = rule_engine.evaluate_scientific_boundary(evidence_payload)
    assert result.passed is True
    assert result.score == 100.0


def test_conflict_preservation_tagged(rule_engine):
    conflicting_records = [
        {"subject_id": "SUBJ-1", "timestamp": "2026-10-01T10:00:00Z", "value": 72.0, "status": "CONFLICT"},
        {"subject_id": "SUBJ-1", "timestamp": "2026-10-01T10:00:00Z", "value": 98.0, "status": "CONFLICT"}
    ]
    result = rule_engine.evaluate_conflict_preservation(conflicting_records)
    assert result.passed is True
    assert result.score == 100.0


def test_conflict_preservation_untagged_penalized(rule_engine):
    conflicting_records = [
        {"subject_id": "SUBJ-1", "timestamp": "2026-10-01T10:00:00Z", "value": 72.0, "status": "ACCEPTED"},
        {"subject_id": "SUBJ-1", "timestamp": "2026-10-01T10:00:00Z", "value": 98.0, "status": "ACCEPTED"}
    ]
    result = rule_engine.evaluate_conflict_preservation(conflicting_records)
    assert result.passed is False
    assert result.score == 20.0


def test_state_hash_determinism(rule_engine):
    payload = {"drug": "TRASTUZUMAB", "assay": "ELISA", "score": 98.4}
    hash_1 = rule_engine.compute_state_hash(payload)
    hash_2 = rule_engine.compute_state_hash(payload)
    assert hash_1 == hash_2
    assert len(hash_1) == 64
