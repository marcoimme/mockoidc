"""
Unit tests per il modulo jwks_service
"""

from jwks_service import JWKSService


class TestJWKSService:
    """Test per il servizio JWKS"""

    def test_jwks_service_initialization(self):
        """Verifica che il servizio si inizializzi correttamente"""
        service = JWKSService()
        assert service.private_key is not None
        assert service.public_key is not None
        assert service.kid is not None

    def test_get_private_key_pem(self):
        """Verifica che la chiave privata sia in formato PEM"""
        service = JWKSService()
        pem = service.get_private_key_pem()

        assert isinstance(pem, str)
        assert pem.startswith("-----BEGIN PRIVATE KEY-----")
        assert pem.endswith("-----END PRIVATE KEY-----\n")

    def test_get_public_key_pem(self):
        """Verifica che la chiave pubblica sia in formato PEM"""
        service = JWKSService()
        pem = service.get_public_key_pem()

        assert isinstance(pem, str)
        assert pem.startswith("-----BEGIN PUBLIC KEY-----")
        assert pem.endswith("-----END PUBLIC KEY-----\n")

    def test_get_public_numbers(self):
        """Verifica che i numeri pubblici siano validi"""
        service = JWKSService()
        n, e = service.get_public_numbers()

        assert isinstance(n, int)
        assert isinstance(e, int)
        assert n > 0
        assert e > 0
        # L'esponente pubblico dovrebbe essere 65537
        assert e == 65537

    def test_get_jwks_structure(self):
        """Verifica la struttura del JWKS"""
        service = JWKSService()
        jwks = service.get_jwks()

        assert "keys" in jwks
        assert isinstance(jwks["keys"], list)
        assert len(jwks["keys"]) == 1

        key = jwks["keys"][0]
        assert key["kty"] == "RSA"
        assert key["use"] == "sig"
        assert key["alg"] == "RS256"
        assert "kid" in key
        assert "n" in key
        assert "e" in key

    def test_get_kid(self):
        """Verifica che il Key ID sia corretto"""
        service = JWKSService()
        kid = service.get_kid()

        assert isinstance(kid, str)
        assert len(kid) > 0

    def test_int_to_base64url(self):
        """Verifica la conversione da intero a base64url"""
        service = JWKSService()

        # Test con valore noto
        value = 65537
        result = service._int_to_base64url(value)

        assert isinstance(result, str)
        assert len(result) > 0
        # base64url non dovrebbe contenere padding '='
        assert "=" not in result

    def test_keys_are_consistent(self):
        """Verifica che le chiavi rimangano consistenti per un'istanza"""
        service = JWKSService()

        jwks1 = service.get_jwks()
        jwks2 = service.get_jwks()

        assert jwks1 == jwks2

    def test_different_instances_have_different_keys(self):
        """Verifica che istanze diverse abbiano chiavi diverse"""
        service1 = JWKSService()
        service2 = JWKSService()

        jwks1 = service1.get_jwks()
        jwks2 = service2.get_jwks()

        # Le chiavi dovrebbero essere diverse
        assert jwks1["keys"][0]["n"] != jwks2["keys"][0]["n"]
