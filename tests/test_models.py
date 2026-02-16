"""
Unit tests per i modelli Pydantic
"""
import pytest
from pydantic import ValidationError
from models import (
    TokenRequest,
    TokenResponse,
    DiscoveryResponse,
    JWK,
    JWKSResponse,
    UserInfoResponse,
    AuthorizationCode
)


class TestTokenRequest:
    """Test per il modello TokenRequest"""
    
    def test_token_request_authorization_code(self):
        """Test per authorization_code grant type"""
        data = {
            "grant_type": "authorization_code",
            "code": "test-code",
            "redirect_uri": "http://localhost:3000/callback",
            "client_id": "test-client"
        }
        request = TokenRequest(**data)
        assert request.grant_type == "authorization_code"
        assert request.code == "test-code"
    
    def test_token_request_refresh_token(self):
        """Test per refresh_token grant type"""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": "test-refresh"
        }
        request = TokenRequest(**data)
        assert request.grant_type == "refresh_token"
        assert request.refresh_token == "test-refresh"
    
    def test_token_request_missing_grant_type(self):
        """Test che grant_type sia obbligatorio"""
        data = {}
        with pytest.raises(ValidationError):
            TokenRequest(**data)


class TestTokenResponse:
    """Test per il modello TokenResponse"""
    
    def test_token_response_valid(self):
        """Test per response valida"""
        data = {
            "access_token": "test-access-token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "id_token": "test-id-token",
            "refresh_token": "test-refresh-token"
        }
        response = TokenResponse(**data)
        assert response.access_token == "test-access-token"
        assert response.token_type == "Bearer"
        assert response.expires_in == 3600
    
    def test_token_response_defaults(self):
        """Test per valori default"""
        data = {
            "access_token": "test-access-token",
            "expires_in": 3600
        }
        response = TokenResponse(**data)
        assert response.token_type == "Bearer"
        assert response.id_token is None
        assert response.refresh_token is None


class TestDiscoveryResponse:
    """Test per il modello DiscoveryResponse"""
    
    def test_discovery_response_valid(self):
        """Test per response valida"""
        data = {
            "issuer": "http://localhost:8080",
            "authorization_endpoint": "http://localhost:8080/authorize",
            "token_endpoint": "http://localhost:8080/token",
            "userinfo_endpoint": "http://localhost:8080/userinfo",
            "jwks_uri": "http://localhost:8080/jwks",
            "revocation_endpoint": "http://localhost:8080/revoke",
            "end_session_endpoint": "http://localhost:8080/logout",
            "response_types_supported": ["code"],
            "scopes_supported": ["openid", "profile", "email"]
        }
        response = DiscoveryResponse(**data)
        assert response.issuer == "http://localhost:8080"
        assert "openid" in response.scopes_supported
    
    def test_discovery_response_defaults(self):
        """Test per valori default"""
        data = {
            "issuer": "http://localhost:8080",
            "authorization_endpoint": "http://localhost:8080/authorize",
            "token_endpoint": "http://localhost:8080/token",
            "userinfo_endpoint": "http://localhost:8080/userinfo",
            "jwks_uri": "http://localhost:8080/jwks",
            "revocation_endpoint": "http://localhost:8080/revoke",
            "end_session_endpoint": "http://localhost:8080/logout",
            "response_types_supported": ["code"],
            "scopes_supported": ["openid"]
        }
        response = DiscoveryResponse(**data)
        assert response.subject_types_supported == ["public"]
        assert "RS256" in response.id_token_signing_alg_values_supported


class TestJWK:
    """Test per il modello JWK"""
    
    def test_jwk_valid(self):
        """Test per JWK valido"""
        data = {
            "kty": "RSA",
            "use": "sig",
            "kid": "test-key-1",
            "n": "test-n-value",
            "e": "AQAB"
        }
        jwk = JWK(**data)
        assert jwk.kty == "RSA"
        assert jwk.alg == "RS256"
    
    def test_jwk_missing_required_field(self):
        """Test che i campi obbligatori siano presenti"""
        data = {
            "kty": "RSA",
            "use": "sig"
        }
        with pytest.raises(ValidationError):
            JWK(**data)


class TestUserInfoResponse:
    """Test per il modello UserInfoResponse"""
    
    def test_userinfo_response_valid(self):
        """Test per response valida"""
        data = {
            "sub": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Test User",
            "email": "test@example.com",
            "oid": "550e8400-e29b-41d4-a716-446655440000"
        }
        response = UserInfoResponse(**data)
        assert response.sub == "550e8400-e29b-41d4-a716-446655440000"
        assert response.email_verified is True  # Default
    
    def test_userinfo_response_optional_fields(self):
        """Test per campi opzionali"""
        data = {
            "sub": "550e8400-e29b-41d4-a716-446655440000"
        }
        response = UserInfoResponse(**data)
        assert response.name is None
        assert response.email is None
        assert response.roles is None


class TestAuthorizationCode:
    """Test per la classe AuthorizationCode"""
    
    def test_authorization_code_creation(self):
        """Test per creazione authorization code"""
        code = AuthorizationCode(
            code="test-code",
            client_id="test-client",
            redirect_uri="http://localhost:3000/callback",
            scope="openid profile",
            user_claims={"sub": "test-user"}
        )
        assert code.code == "test-code"
        assert code.client_id == "test-client"
        assert code.scope == "openid profile"
    
    def test_authorization_code_with_pkce(self):
        """Test per authorization code con PKCE"""
        code = AuthorizationCode(
            code="test-code",
            client_id="test-client",
            redirect_uri="http://localhost:3000/callback",
            scope="openid profile",
            user_claims={"sub": "test-user"},
            code_challenge="test-challenge",
            code_challenge_method="S256"
        )
        assert code.code_challenge == "test-challenge"
        assert code.code_challenge_method == "S256"
    
    def test_authorization_code_with_nonce(self):
        """Test per authorization code con nonce"""
        code = AuthorizationCode(
            code="test-code",
            client_id="test-client",
            redirect_uri="http://localhost:3000/callback",
            scope="openid profile",
            user_claims={"sub": "test-user"},
            nonce="test-nonce"
        )
        assert code.nonce == "test-nonce"
