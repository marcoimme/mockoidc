"""
Pytest configuration and shared fixtures
"""

import os
import sys

import pytest
from starlette.testclient import TestClient

# Aggiungi la directory root al path per importare i moduli
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="function")
def test_client():
    """Fixture per il client di test FastAPI"""
    from main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_user_email():
    """Email di test per utente mock"""
    return "test.user@example.com"


@pytest.fixture
def sample_user_claims():
    """Claims di test per utente mock"""
    return {
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "oid": "550e8400-e29b-41d4-a716-446655440000",
        "tid": "9188040d-6c67-4c5b-b112-36a304b66dad",
        "name": "Test User",
        "given_name": "Test",
        "family_name": "User",
        "email": "test.user@example.com",
        "upn": "test.user@example.com",
        "preferred_username": "test.user@example.com",
        "roles": ["User"],
        "groups": ["default-group"],
    }


@pytest.fixture
def auth_params():
    """Parametri standard per authorization request"""
    return {
        "response_type": "code",
        "client_id": "test-client",
        "redirect_uri": "http://localhost:3000/callback",
        "scope": "openid profile email",
        "state": "test-state-123",
    }


@pytest.fixture
def pkce_params():
    """Parametri PKCE per authorization request"""
    return {"code_challenge": "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM", "code_challenge_method": "S256"}
