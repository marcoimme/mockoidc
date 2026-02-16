"""
Unit tests per il modulo claims_generator
"""

from claims_generator import generate_claims_from_email, generate_deterministic_uuid


class TestGenerateClaimsFromEmail:
    """Test per la funzione generate_claims_from_email"""

    def test_generate_claims_basic(self):
        """Verifica che vengano generati i claims base"""
        email = "test.user@example.com"
        claims = generate_claims_from_email(email)

        # Verifica campi obbligatori
        assert "sub" in claims
        assert "oid" in claims
        assert "tid" in claims
        assert "email" in claims
        assert "name" in claims
        assert "given_name" in claims
        assert "family_name" in claims
        assert "upn" in claims
        assert "preferred_username" in claims
        assert "roles" in claims
        assert "groups" in claims

        # Verifica valori
        assert claims["email"] == email
        assert claims["upn"] == email
        assert claims["preferred_username"] == email

    def test_generate_claims_name_parsing_with_dot(self):
        """Verifica il parsing del nome con punto"""
        email = "mario.rossi@example.com"
        claims = generate_claims_from_email(email)

        assert claims["given_name"] == "Mario"
        assert claims["family_name"] == "Rossi"
        assert claims["name"] == "Mario Rossi"

    def test_generate_claims_name_parsing_with_underscore(self):
        """Verifica il parsing del nome con underscore"""
        email = "john_doe@example.com"
        claims = generate_claims_from_email(email)

        assert claims["given_name"] == "John"
        assert claims["family_name"] == "Doe"
        assert claims["name"] == "John Doe"

    def test_generate_claims_name_parsing_with_hyphen(self):
        """Verifica il parsing del nome con trattino"""
        email = "mary-jane@example.com"
        claims = generate_claims_from_email(email)

        assert claims["given_name"] == "Mary"
        assert claims["family_name"] == "Jane"
        assert claims["name"] == "Mary Jane"

    def test_generate_claims_single_name(self):
        """Verifica il parsing con un solo nome"""
        email = "admin@example.com"
        claims = generate_claims_from_email(email)

        assert "given_name" in claims
        assert "family_name" in claims
        assert claims["name"] != ""

    def test_generate_claims_with_numbers(self):
        """Verifica il parsing con numeri nell'email"""
        email = "user123@example.com"
        claims = generate_claims_from_email(email)

        assert claims["email"] == email
        assert "given_name" in claims
        assert "family_name" in claims

    def test_generate_claims_deterministic(self):
        """Verifica che i claims siano deterministici"""
        email = "test@example.com"
        claims1 = generate_claims_from_email(email)
        claims2 = generate_claims_from_email(email)

        # Lo stesso email dovrebbe generare gli stessi claims
        assert claims1["sub"] == claims2["sub"]
        assert claims1["oid"] == claims2["oid"]
        assert claims1["tid"] == claims2["tid"]

    def test_generate_claims_different_emails_different_ids(self):
        """Verifica che email diverse generino ID diversi"""
        email1 = "user1@example.com"
        email2 = "user2@example.com"

        claims1 = generate_claims_from_email(email1)
        claims2 = generate_claims_from_email(email2)

        assert claims1["sub"] != claims2["sub"]
        assert claims1["oid"] != claims2["oid"]

    def test_generate_claims_same_domain_same_tid(self):
        """Verifica che email dello stesso dominio abbiano stesso tid"""
        email1 = "user1@example.com"
        email2 = "user2@example.com"

        claims1 = generate_claims_from_email(email1)
        claims2 = generate_claims_from_email(email2)

        # Stesso dominio = stesso tenant ID
        assert claims1["tid"] == claims2["tid"]

    def test_generate_claims_different_domain_different_tid(self):
        """Verifica che email di domini diversi abbiano tid diversi"""
        email1 = "user@example.com"
        email2 = "user@different.com"

        claims1 = generate_claims_from_email(email1)
        claims2 = generate_claims_from_email(email2)

        # Dominio diverso = tenant ID diverso
        assert claims1["tid"] != claims2["tid"]

    def test_generate_claims_roles_and_groups(self):
        """Verifica che vengano assegnati ruoli e gruppi di default"""
        email = "test@example.com"
        claims = generate_claims_from_email(email)

        assert isinstance(claims["roles"], list)
        assert isinstance(claims["groups"], list)
        assert len(claims["roles"]) > 0
        assert len(claims["groups"]) > 0

    def test_generate_claims_uuid_format(self):
        """Verifica che sub, oid e tid siano UUID validi"""
        import re

        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

        email = "test@example.com"
        claims = generate_claims_from_email(email)

        assert re.match(uuid_pattern, claims["sub"])
        assert re.match(uuid_pattern, claims["oid"])
        assert re.match(uuid_pattern, claims["tid"])

    def test_generate_claims_sub_equals_oid(self):
        """Verifica che sub e oid siano uguali (come in Azure AD)"""
        email = "test@example.com"
        claims = generate_claims_from_email(email)

        assert claims["sub"] == claims["oid"]


class TestGenerateDeterministicUUID:
    """Test per la funzione generate_deterministic_uuid"""

    def test_generate_uuid_returns_string(self):
        """Verifica che venga restituita una stringa"""
        uuid_str = generate_deterministic_uuid("test")
        assert isinstance(uuid_str, str)

    def test_generate_uuid_valid_format(self):
        """Verifica che l'UUID sia in formato valido"""
        import re

        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

        uuid_str = generate_deterministic_uuid("test")
        assert re.match(uuid_pattern, uuid_str)

    def test_generate_uuid_deterministic(self):
        """Verifica che sia deterministico"""
        seed = "test-seed"
        uuid1 = generate_deterministic_uuid(seed)
        uuid2 = generate_deterministic_uuid(seed)

        assert uuid1 == uuid2

    def test_generate_uuid_different_seeds(self):
        """Verifica che seed diversi generino UUID diversi"""
        uuid1 = generate_deterministic_uuid("seed1")
        uuid2 = generate_deterministic_uuid("seed2")

        assert uuid1 != uuid2
