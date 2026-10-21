"""
Unit Tests for Security Middleware & Error Boundary Protection
"""
import pytest
from fastapi import HTTPException
from security.middleware import (
    register_used_token,
    is_token_replayed,
    clear_token_cache,
    UserRole
)


def test_token_registration_and_replay_detection():
    token = "audit-sig-unique-12345"
    assert is_token_replayed(token) is False
    register_used_token(token)
    assert is_token_replayed(token) is True

    # Replay must raise HTTP 409 Conflict
    with pytest.raises(HTTPException) as exc_info:
        register_used_token(token)
    assert exc_info.value.status_code == 409
    assert "REPLAY_REJECTED" in exc_info.value.detail


def test_user_roles_enumeration():
    assert UserRole.AUDITOR.value == "Auditor"
    assert UserRole.GOVERNOR.value == "Governor"
    assert UserRole.ANSH_AUDIT_LEAD.value == "Ansh_Audit_Lead"
