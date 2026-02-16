from typing import Dict, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configurazione del mock OIDC server"""
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Host del server")
    port: int = Field(default=8080, description="Porta del server")

    
    # Token settings
    access_token_expiry: int = Field(default=3600, description="Scadenza access token in secondi")
    id_token_expiry: int = Field(default=3600, description="Scadenza id token in secondi")
    authorization_code_expiry: int = Field(default=600, description="Scadenza authorization code in secondi")
    
    # Supported features
    supported_scopes: List[str] = Field(
        default=["openid", "profile", "email", "offline_access"],
        description="Scopes supportati"
    )
    supported_response_types: List[str] = Field(
        default=["code", "token", "id_token", "code id_token", "code token", "id_token token", "code id_token token"],
        description="Response types supportati"
    )
    supported_grant_types: List[str] = Field(
        default=["authorization_code", "refresh_token"],
        description="Grant types supportati"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Mock users configuration (opzionale - se None, qualsiasi credenziale viene accettata)
# Imposta a None per accettare qualsiasi email/password e generare claims dinamici
MOCK_USERS = None  # Accetta qualsiasi credenziale

# Mock users pre-configurati (commentato - usa solo se vuoi utenti specifici)
# MOCK_USERS = [
#     {
#         "username": "user1@example.com",
#         "password": "password1",
#         "claims": {
#             "sub": "00000000-0000-0000-0000-000000000001",
#             "oid": "00000000-0000-0000-0000-000000000001",
#             "tid": "11111111-1111-1111-1111-111111111111",
#             "name": "Test User One",
#             "given_name": "Test",
#             "family_name": "User One",
#             "email": "user1@example.com",
#             "upn": "user1@example.com",
#             "preferred_username": "user1@example.com",
#             "roles": ["User", "Reader"],
#             "groups": ["group1", "group2"]
#         }
#     },
#     {
#         "username": "admin@example.com",
#         "password": "admin123",
#         "claims": {
#             "sub": "00000000-0000-0000-0000-000000000002",
#             "oid": "00000000-0000-0000-0000-000000000002",
#             "tid": "11111111-1111-1111-1111-111111111111",
#             "name": "Admin User",
#             "given_name": "Admin",
#             "family_name": "User",
#             "email": "admin@example.com",
#             "upn": "admin@example.com",
#             "preferred_username": "admin@example.com",
#             "roles": ["Admin", "User", "Writer"],
#             "groups": ["group1", "admin-group"]
#         }
#     }
# ]

# Configurazione claims dinamici
DYNAMIC_CLAIMS_CONFIG = {
    "default_tenant_id": "11111111-1111-1111-1111-111111111111",
    "default_roles": ["User"],
    "default_groups": ["default-group"],
}


settings = Settings()
