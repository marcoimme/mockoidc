"""
Token Service - Gestione generazione e validazione JWT
"""
import time
import hashlib
import base64
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import jwt, JWTError
from jwks_service import jwks_service
from config import settings


class TokenService:
    """Servizio per la gestione dei token JWT"""
    
    def __init__(self):
        self.jwks_service = jwks_service
    
    def generate_authorization_code(self, length: int = 32) -> str:
        """Genera un authorization code casuale"""
        return secrets.token_urlsafe(length)
    
    def generate_refresh_token(self, length: int = 32) -> str:
        """Genera un refresh token casuale"""
        return f"refresh_{secrets.token_urlsafe(length)}"
    
    def generate_access_token(
        self,
        user_claims: Dict,
        scope: str,
        issuer: Optional[str] = None
    ) -> str:
        """
        Genera un access token JWT
        
        Args:
            user_claims: Claims dell'utente
            scope: Scopes richiesti
            issuer: Issuer del token (se None, usa settings.issuer)
        
        Returns:
            JWT firmato
        """
        now = int(time.time())
        exp = now + settings.access_token_expiry
        
        # Costruisci i claims del token
        claims = {
            "iss": issuer or settings.issuer,
            "sub": user_claims.get("sub"),
            "aud": "api://default",
            "iat": now,
            "exp": exp,
            "scope": scope,
            # Azure AD compatible claims
            "oid": user_claims.get("oid"),
            "tid": user_claims.get("tid"),
            "upn": user_claims.get("upn"),
            "name": user_claims.get("name"),
            "email": user_claims.get("email"),
            "preferred_username": user_claims.get("preferred_username"),
            "roles": user_claims.get("roles", []),
            "groups": user_claims.get("groups", [])
        }
        
        # Firma il token con la chiave privata
        token = jwt.encode(
            claims,
            self.jwks_service.get_private_key_pem(),
            algorithm="RS256",
            headers={"kid": self.jwks_service.get_kid()}
        )
        
        return token
    
    def generate_id_token(
        self,
        user_claims: Dict,
        client_id: str,
        nonce: Optional[str] = None,
        issuer: Optional[str] = None
    ) -> str:
        """
        Genera un ID token JWT
        
        Args:
            user_claims: Claims dell'utente
            client_id: Client ID dell'applicazione
            nonce: Nonce opzionale
            issuer: Issuer del token (se None, usa settings.issuer)
        
        Returns:
            JWT firmato
        """
        now = int(time.time())
        exp = now + settings.id_token_expiry
        
        # Costruisci i claims del token
        claims = {
            "iss": issuer or settings.issuer,
            "sub": user_claims.get("sub"),
            "aud": client_id,
            "iat": now,
            "exp": exp,
            "auth_time": now,
            # OpenID Connect standard claims
            "name": user_claims.get("name"),
            "given_name": user_claims.get("given_name"),
            "family_name": user_claims.get("family_name"),
            "email": user_claims.get("email"),
            "email_verified": True,
            # Azure AD compatible claims
            "oid": user_claims.get("oid"),
            "tid": user_claims.get("tid"),
            "upn": user_claims.get("upn"),
            "preferred_username": user_claims.get("preferred_username"),
        }
        
        if nonce:
            claims["nonce"] = nonce
        
        # Firma il token con la chiave privata
        token = jwt.encode(
            claims,
            self.jwks_service.get_private_key_pem(),
            algorithm="RS256",
            headers={"kid": self.jwks_service.get_kid()}
        )
        
        return token
    
    def decode_token(self, token: str) -> Dict:
        """
        Decodifica e valida un JWT
        
        Args:
            token: JWT da decodificare
        
        Returns:
            Claims del token
        
        Raises:
            JWTError: Se il token non è valido
        """
        try:
            # Decodifica senza verifica audience (per mock server)
            claims = jwt.decode(
                token,
                self.jwks_service.get_public_key_pem(),
                algorithms=["RS256"],
                options={
                    "verify_signature": True,
                    "verify_aud": False,  # Non verifica audience in mock
                    "verify_exp": True
                }
            )
            return claims
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    def validate_pkce(
        self,
        code_verifier: str,
        code_challenge: str,
        code_challenge_method: str
    ) -> bool:
        """
        Valida PKCE (Proof Key for Code Exchange)
        
        Args:
            code_verifier: Verifier inviato dal client
            code_challenge: Challenge salvato durante authorize
            code_challenge_method: Metodo usato (plain o S256)
        
        Returns:
            True se valido, False altrimenti
        """
        if code_challenge_method == "plain":
            return code_verifier == code_challenge
        
        elif code_challenge_method == "S256":
            # Calcola l'hash SHA256 del verifier
            verifier_hash = hashlib.sha256(code_verifier.encode()).digest()
            # Converti in base64url
            verifier_challenge = base64.urlsafe_b64encode(verifier_hash).rstrip(b'=').decode('utf-8')
            return verifier_challenge == code_challenge
        
        return False


# Istanza globale del servizio
token_service = TokenService()
