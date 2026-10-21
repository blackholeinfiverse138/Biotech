"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
import os
from starlette.testclient import TestClient

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.production import app
from evaluation_engine.rule_engine import BiotechRuleEngine
from task_selector.review_orchestrator import BiotechReviewOrchestrator
from integrations.local_llm_client import LocalLLMClient
from security.middleware import clear_token_cache


@pytest.fixture(autouse=True)
def clean_security_tokens():
    clear_token_cache()
    yield
    clear_token_cache()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def rule_engine():
    return BiotechRuleEngine()


@pytest.fixture
def review_orchestrator():
    return BiotechReviewOrchestrator()


@pytest.fixture
def llm_client():
    return LocalLLMClient()
