"""
Integration Tests for 50-Run Deterministic State Hash Verification
===================================================================
Parikshak Strict Acceptance Gate:
"Deterministic execution: 50 consecutive runs must produce identical SHA-256 state hashes"
"""
import pytest
from evaluation_engine.rule_engine import BiotechRuleEngine


def test_fifty_consecutive_runs_deterministic_sha256():
    """
    Executes 50 independent evaluations on identical input payloads
    and verifies that every single execution generates the EXACT same SHA-256 hash.
    """
    engine = BiotechRuleEngine()
    test_payload = {
        "candidate": "Shamit",
        "capability": "TB Drug-Discovery Candidate Intelligence",
        "molecular_target": "InhA",
        "smiles": "CC1=CN=C(C(=O)N)C=C1",
        "pIC50": 7.42,
        "lipinski_violations": 0,
        "is_synthetic": False
    }

    hashes = []
    for iteration in range(50):
        # 1. Evaluate payload
        rubric = engine.evaluate_full_submission(
            capability="TB Drug-Discovery Candidate Intelligence",
            payload=test_payload
        )
        # 2. Compute canonical hash of result
        state_hash = engine.compute_state_hash({
            "iteration_input": test_payload,
            "rubric_score": rubric.composite_score,
            "rubric_result": rubric.evaluation_result
        })
        hashes.append(state_hash)

    # Assert 50 runs were executed
    assert len(hashes) == 50

    # Assert ALL 50 hashes are identical
    unique_hashes = set(hashes)
    assert len(unique_hashes) == 1, f"Determinism failure: Generated {len(unique_hashes)} distinct hashes across 50 runs: {unique_hashes}"

    canonical_hash = hashes[0]
    assert len(canonical_hash) == 64
    print(f"\n[50-RUN VERIFICATION SUCCESS] Canonical SHA-256 Hash: {canonical_hash}")


def test_50_consecutive_runs_pravah_streaming_deterministic_hash():
    """Verify that 50 consecutive runs of Pravah streaming state hashing produce identical SHA-256 hashes."""
    from evaluation_engine.pravah_streaming import PravahReplayEngine, PravahEventType
    engine = PravahReplayEngine(ledger_path="storage/test_biotech_det_pravah.jsonl")
    engine.reset_for_tests()
    for i in range(1, 4):
        engine.append_event(
            trace_id=f"trace-fixed-{i}",
            event_type=PravahEventType.DATASET_INGESTION,
            payload={"dataset": f"biotech_{i}"},
            event_id=f"evt-fixed-{i:06d}"
        )

    hashes = []
    for _ in range(50):
        h = engine.compute_ledger_state_hash()
        hashes.append(h)

    engine.reset_for_tests()
    assert len(hashes) == 50
    assert len(set(hashes)) == 1
    assert len(hashes[0]) == 64


def test_50_consecutive_runs_concurrency_governance_deterministic_hash():
    """Verify that 50 consecutive runs of Concurrency Governance state hashing produce identical SHA-256 hashes."""
    from task_selector.state_machine import ConcurrencyGovernanceEngine, GovernanceLifecycleState
    engine = ConcurrencyGovernanceEngine()
    engine.reset_for_tests()
    engine.register_entity(entity_id="ds_bio_det_01", initial_state=GovernanceLifecycleState.INIT)
    engine.register_entity(entity_id="ds_bio_det_02", initial_state=GovernanceLifecycleState.VALIDATING)

    hashes = []
    for _ in range(50):
        h = engine.compute_state_hash()
        hashes.append(h)

    engine.reset_for_tests()
    assert len(hashes) == 50
    assert len(set(hashes)) == 1
    assert len(hashes[0]) == 64
