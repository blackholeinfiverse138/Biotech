"""
Unit Tests for BiotechReviewOrchestrator
"""
import pytest
from task_selector.review_orchestrator import (
    BiotechReviewOrchestrator,
    ReviewPacketContract,
    ReviewStage,
    DecisionState
)


@pytest.fixture
def sample_packet():
    return ReviewPacketContract(
        candidate_name="Sara",
        capability_name="Formulation & Stability Evidence Intelligence",
        entry_point="src/formulation_pipeline.py",
        core_execution_flow="Input -> Kinetic Math -> Shelf-Life Estimation -> Storage",
        runtime_flow="FastAPI endpoint /api/stability",
        real_output={
            "drug_name": "ADALIMUMAB",
            "adverse_event": "None",
            "stability_score": 96.5,
            "shelf_life_months": 24,
            "is_synthetic": False
        },
        what_changed="Added Arrhenius rate constant validation",
        failure_cases=["Extreme pH test", "Zero concentration"],
        test_results={"unit_tests": "24/24 passed", "coverage": "94%"},
        integration_contract="JSON schema v1.0",
        known_limitations=["Temperature bounds restricted to 2-40C"],
        evidence_uris=["s3://biotech-audit/sara/run_01.log"]
    )


def test_start_candidate_review_flow(review_orchestrator, sample_packet):
    record = review_orchestrator.start_candidate_review(
        candidate_name=sample_packet.candidate_name,
        capability=sample_packet.capability_name,
        packet_contract=sample_packet
    )
    assert record.review_id.startswith("REV-SARA-")
    assert record.candidate_name == "Sara"
    assert record.decision_state in [DecisionState.APPROVED, DecisionState.APPROVED_WITH_FIXES]
    assert record.current_stage == ReviewStage.STAGE_3_INDEPENDENT_AUDIT
    assert len(record.state_hash) == 64


def test_section_16_disagreement_recording(review_orchestrator, sample_packet):
    record = review_orchestrator.start_candidate_review(
        candidate_name=sample_packet.candidate_name,
        capability=sample_packet.capability_name,
        packet_contract=sample_packet
    )
    
    updated = review_orchestrator.record_section_16_disagreement(
        review_id=record.review_id,
        observation="Missing Arrhenius temperature bounds check in candidate execution path.",
        evidence="Observed extrapolation up to 100C without warning in logs.",
        differing_interpretation="Raj considered temperature bounds an integration detail; Ansh views it as critical data integrity constraint.",
        required_verification="Add explicit 2-40C range validator before Stage 6 integration."
    )

    assert len(updated.disagreements) == 1
    assert updated.disagreements[0].observation.startswith("Missing Arrhenius")
    assert updated.decision_state in [DecisionState.APPROVED_WITH_FIXES, DecisionState.REVISION_REQUIRED]


def test_advance_stage_workflow(review_orchestrator, sample_packet):
    record = review_orchestrator.start_candidate_review(
        candidate_name=sample_packet.candidate_name,
        capability=sample_packet.capability_name,
        packet_contract=sample_packet
    )
    
    advanced = review_orchestrator.advance_stage(record.review_id, ReviewStage.STAGE_6_INTEGRATE)
    assert advanced.current_stage == ReviewStage.STAGE_6_INTEGRATE


def test_finalize_decision(review_orchestrator, sample_packet):
    record = review_orchestrator.start_candidate_review(
        candidate_name=sample_packet.candidate_name,
        capability=sample_packet.capability_name,
        packet_contract=sample_packet
    )

    finalized = review_orchestrator.finalize_decision(record.review_id, DecisionState.APPROVED)
    assert finalized.decision_state == DecisionState.APPROVED
    assert finalized.current_stage == ReviewStage.STAGE_9_HANDOVER
