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
