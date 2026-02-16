import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from typing import Tuple
import hashlib


class JWKSService:
    """Servizio per la gestione delle chiavi RSA e JWKS"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.kid = "mock-oidc-key-1"
        self._generate_keys()
    
    def _generate_keys(self):
        """Genera una coppia di chiavi RSA"""
        # Genera chiave privata RSA
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Estrai la chiave pubblica
        self.public_key = self.private_key.public_key()
    
    def get_private_key_pem(self) -> str:
        """Restituisce la chiave privata in formato PEM"""
        pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode('utf-8')
    
    def get_public_key_pem(self) -> str:
        """Restituisce la chiave pubblica in formato PEM"""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    
    def get_public_numbers(self) -> Tuple[int, int]:
        """Restituisce i numeri pubblici (n, e) della chiave RSA"""
        public_numbers = self.public_key.public_numbers()
        return public_numbers.n, public_numbers.e
    
    def _int_to_base64url(self, value: int) -> str:
        """Converte un intero in base64url encoding"""
        # Converti l'intero in bytes
        value_bytes = value.to_bytes(
            (value.bit_length() + 7) // 8, 
            byteorder='big'
        )
        # Converti in base64url
        return base64.urlsafe_b64encode(value_bytes).rstrip(b'=').decode('utf-8')
    
    def get_jwks(self) -> dict:
        """Restituisce il JWKS (JSON Web Key Set)"""
        n, e = self.get_public_numbers()
        
        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "kid": self.kid,
                    "alg": "RS256",
                    "n": self._int_to_base64url(n),
                    "e": self._int_to_base64url(e)
                }
            ]
        }
    
    def get_kid(self) -> str:
        """Restituisce il Key ID"""
        return self.kid


# Istanza globale del servizio
jwks_service = JWKSService()
