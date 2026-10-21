"""
Unit Tests for LocalLLMClient & Deterministic Fallback
"""
import pytest
from integrations.local_llm_client import LocalLLMClient


def test_deterministic_rule_extract(llm_client):
    text = "Patient developed severe headache and rash after taking 400mg IBUPROFEN."
    res = llm_client.verify_biotech_text(text)
    assert res.verified is True
    assert "IBUPROFEN" in res.extracted_entities
    assert "Headache" in res.adverse_events
    assert "Rash" in res.adverse_events
    assert len(res.deterministic_hash) == 64


def test_llm_client_caching_determinism(llm_client):
    text = "Formulation study for RIFAMPICIN in combination with ISONIAZID."
    res1 = llm_client.verify_biotech_text(text)
    res2 = llm_client.verify_biotech_text(text)
    assert res1.deterministic_hash == res2.deterministic_hash
    assert res1.extracted_entities == res2.extracted_entities
