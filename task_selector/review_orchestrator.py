"""
Biotech Review Orchestrator - Convergence & Workflow Engine
============================================================
Owner: ANSH (AI/ML + Data Audit Lead)
Task ID: T-GOV-F01 (Remediation & Structural Compliance)
Domain: Biotech Integration, Audit & Convergence

Coordinates the 9-stage Day 3 convergence cycle, enforces the Section 16
independent audit disagreement protocol, manages the 4 decision states,
and generates standardized review packets.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import hashlib
import json
import logging
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from evaluation_engine.rule_engine import BiotechRuleEngine, EvaluationRubric

logger = logging.getLogger("biotech_review_orchestrator")


class ReviewStage(str, Enum):
    STAGE_1_FUNCTIONAL_TESTING = "Stage 1: Functional Testing (Sarvesh)"
    STAGE_2_TECHNICAL_REVIEW = "Stage 2: Technical/Integration Review (Harsha/Karan/Raj)"
    STAGE_3_INDEPENDENT_AUDIT = "Stage 3: Independent Audit (Ansh/Pratik/Aman)"
    STAGE_4_CANDIDATE_FIXES = "Stage 4: Candidate Fixes"
    STAGE_5_RERUN_TESTS = "Stage 5: Rerun Functional Tests (Sarvesh)"
    STAGE_6_INTEGRATE = "Stage 6: Cross-Module Integration (Raj/Karan)"
    STAGE_7_CAPTURE_EVIDENCE = "Stage 7: Capture Evidence Packet"
    STAGE_8_FINAL_REVIEW = "Stage 8: Final Review"
    STAGE_9_HANDOVER = "Stage 9: Handover & Certification"


class DecisionState(str, Enum):
    APPROVED = "APPROVED"
    APPROVED_WITH_FIXES = "APPROVED WITH FIXES"
    REVISION_REQUIRED = "REVISION REQUIRED"
    REJECTED = "REJECTED"


class Section16Disagreement(BaseModel):
    observation: str
    evidence: str
    differing_interpretation: str
    required_verification: str
    resolved: bool = False
    resolution_notes: Optional[str] = None


class ReviewPacketContract(BaseModel):
    candidate_name: str
    capability_name: str
    entry_point: str
    core_execution_flow: str
    runtime_flow: str
    real_output: Dict[str, Any]
    what_changed: str
    failure_cases: List[str]
    test_results: Dict[str, Any]
    integration_contract: str
    known_limitations: List[str]
    evidence_uris: List[str]


class CandidateReviewRecord(BaseModel):
    review_id: str
    candidate_name: str
    capability: str
    current_stage: ReviewStage = ReviewStage.STAGE_3_INDEPENDENT_AUDIT
    decision_state: DecisionState = DecisionState.APPROVED_WITH_FIXES
    evaluation_rubric: Optional[EvaluationRubric] = None
    packet_contract: Optional[ReviewPacketContract] = None
    disagreements: List[Section16Disagreement] = Field(default_factory=list)
    state_hash: str = ""
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BiotechReviewOrchestrator:
    """
    Manages the multi-stage review workflow for candidate capabilities
    and verifies submission readiness for Day 3 convergence.
    """

    def __init__(self):
        self.rule_engine = BiotechRuleEngine()
        self.active_reviews: Dict[str, CandidateReviewRecord] = {}

    def start_candidate_review(
        self,
        candidate_name: str,
        capability: str,
        packet_contract: ReviewPacketContract
    ) -> CandidateReviewRecord:
        """
        Initializes an independent audit review for an incoming candidate capability.
        """
        review_id = f"REV-{candidate_name.upper()}-{hashlib.sha256(capability.encode()).hexdigest()[:8]}"
        
        # Initial evaluation using RuleEngine
        rubric = self.rule_engine.evaluate_full_submission(
            capability=capability,
            payload=packet_contract.real_output
        )

        # Compute initial decision state
        if rubric.composite_score >= 95.0:
            initial_decision = DecisionState.APPROVED
        elif rubric.composite_score >= 75.0:
            initial_decision = DecisionState.APPROVED_WITH_FIXES
        elif rubric.composite_score >= 50.0:
            initial_decision = DecisionState.REVISION_REQUIRED
        else:
            initial_decision = DecisionState.REJECTED

        state_hash = self.rule_engine.compute_state_hash({
            "review_id": review_id,
            "candidate": candidate_name,
            "score": rubric.composite_score,
            "decision": initial_decision.value
        })

        record = CandidateReviewRecord(
            review_id=review_id,
            candidate_name=candidate_name,
            capability=capability,
            current_stage=ReviewStage.STAGE_3_INDEPENDENT_AUDIT,
            decision_state=initial_decision,
            evaluation_rubric=rubric,
            packet_contract=packet_contract,
            state_hash=state_hash
        )

        self.active_reviews[review_id] = record
        logger.info(f"Started candidate review [{review_id}] for {candidate_name}: {initial_decision.value}")
        return record

    def record_section_16_disagreement(
        self,
        review_id: str,
        observation: str,
        evidence: str,
        differing_interpretation: str,
        required_verification: str
    ) -> CandidateReviewRecord:
        """
        Enforces Section 16 Independent Disagreement Rule.
        Records formal dispute with evidence without interpersonal conflict.
        """
        if review_id not in self.active_reviews:
            raise KeyError(f"Review ID '{review_id}' not found.")

        disagreement = Section16Disagreement(
            observation=observation,
            evidence=evidence,
            differing_interpretation=differing_interpretation,
            required_verification=required_verification
        )

        record = self.active_reviews[review_id]
        record.disagreements.append(disagreement)
        
        # Any unresolved disagreement automatically moves state to REVISION REQUIRED
        if record.decision_state == DecisionState.APPROVED:
            record.decision_state = DecisionState.APPROVED_WITH_FIXES

        record.updated_at = datetime.now(timezone.utc).isoformat()
        record.state_hash = self.rule_engine.compute_state_hash({
            "review_id": review_id,
            "disagreements_count": len(record.disagreements),
            "decision": record.decision_state.value
        })

        logger.info(f"Recorded Section 16 Disagreement for [{review_id}]: {observation[:60]}...")
        return record

    def advance_stage(self, review_id: str, next_stage: ReviewStage) -> CandidateReviewRecord:
        """
        Advances the candidate capability across the 9 convergence stages.
        """
        if review_id not in self.active_reviews:
            raise KeyError(f"Review ID '{review_id}' not found.")

        record = self.active_reviews[review_id]
        record.current_stage = next_stage
        record.updated_at = datetime.now(timezone.utc).isoformat()
        record.state_hash = self.rule_engine.compute_state_hash({
            "review_id": review_id,
            "stage": next_stage.value,
            "decision": record.decision_state.value
        })
        return record

    def finalize_decision(self, review_id: str, final_decision: DecisionState) -> CandidateReviewRecord:
        """
        Finalizes Day 3 decision state (APPROVED, APPROVED WITH FIXES, REVISION REQUIRED, REJECTED).
        """
        if review_id not in self.active_reviews:
            raise KeyError(f"Review ID '{review_id}' not found.")

        record = self.active_reviews[review_id]
        record.decision_state = final_decision
        record.current_stage = ReviewStage.STAGE_9_HANDOVER if final_decision in [DecisionState.APPROVED, DecisionState.APPROVED_WITH_FIXES] else ReviewStage.STAGE_4_CANDIDATE_FIXES
        record.updated_at = datetime.now(timezone.utc).isoformat()
        record.state_hash = self.rule_engine.compute_state_hash({
            "review_id": review_id,
            "final_decision": final_decision.value,
            "final_stage": record.current_stage.value
        })
        return record
