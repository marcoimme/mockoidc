from typing import Optional, List
from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    """Request per il token endpoint"""
    grant_type: str
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    code_verifier: Optional[str] = None
    refresh_token: Optional[str] = None


class TokenResponse(BaseModel):
    """Response del token endpoint"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    id_token: Optional[str] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class DiscoveryResponse(BaseModel):
    """Response del discovery endpoint"""
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    jwks_uri: str
    revocation_endpoint: str
    end_session_endpoint: str
    response_types_supported: List[str]
    subject_types_supported: List[str] = ["public"]
    id_token_signing_alg_values_supported: List[str] = ["RS256"]
    scopes_supported: List[str]
    token_endpoint_auth_methods_supported: List[str] = ["client_secret_post", "client_secret_basic", "none"]
    claims_supported: List[str] = [
        "sub", "iss", "aud", "exp", "iat", "auth_time", "nonce",
        "name", "given_name", "family_name", "email", "email_verified",
        "oid", "tid", "upn", "preferred_username", "roles", "groups"
    ]
    code_challenge_methods_supported: List[str] = ["plain", "S256"]


class JWK(BaseModel):
    """JSON Web Key"""
    kty: str
    use: str
    kid: str
    n: str
    e: str
    alg: str = "RS256"


class JWKSResponse(BaseModel):
    """JWKS response"""
    keys: List[JWK]


class UserInfoResponse(BaseModel):
    """Response del userinfo endpoint"""
    sub: str
    name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = True
    oid: Optional[str] = None
    tid: Optional[str] = None
    upn: Optional[str] = None
    preferred_username: Optional[str] = None
    roles: Optional[List[str]] = None
    groups: Optional[List[str]] = None


class AuthorizationCode:
    """Authorization code con i dati associati"""
    def __init__(
        self,
        code: str,
        client_id: str,
        redirect_uri: str,
        scope: str,
        user_claims: dict,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        nonce: Optional[str] = None
    ):
        self.code = code
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.user_claims = user_claims
        self.code_challenge = code_challenge
        self.code_challenge_method = code_challenge_method
        self.nonce = nonce
