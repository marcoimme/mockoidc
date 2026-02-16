"""
Unit tests per il modulo config
"""

from config import DYNAMIC_CLAIMS_CONFIG, MOCK_USERS, Settings


class TestSettings:
    """Test per la classe Settings"""

    def test_settings_defaults(self):
        """Verifica i valori di default delle impostazioni"""
        settings = Settings()

        assert settings.host == "0.0.0.0"
        assert settings.port == 8080

    def test_settings_token_expiry_defaults(self):
        """Verifica i valori di default per la scadenza dei token"""
        settings = Settings()

        assert settings.access_token_expiry == 3600
        assert settings.id_token_expiry == 3600
        assert settings.authorization_code_expiry == 600

    def test_settings_supported_scopes(self):
        """Verifica gli scopes supportati"""
        settings = Settings()

        assert "openid" in settings.supported_scopes
        assert "profile" in settings.supported_scopes
        assert "email" in settings.supported_scopes
        assert "offline_access" in settings.supported_scopes

    def test_settings_supported_response_types(self):
        """Verifica i response types supportati"""
        settings = Settings()

        assert "code" in settings.supported_response_types
        assert "token" in settings.supported_response_types
        assert "id_token" in settings.supported_response_types

    def test_settings_supported_grant_types(self):
        """Verifica i grant types supportati"""
        settings = Settings()

        assert "authorization_code" in settings.supported_grant_types
        assert "refresh_token" in settings.supported_grant_types


class TestMockUsersConfiguration:
    """Test per la configurazione degli utenti mock"""

    def test_mock_users_is_none_by_default(self):
        """Verifica che MOCK_USERS sia None di default (modalità dinamica)"""
        # In modalità dinamica, qualsiasi credenziale viene accettata
        assert MOCK_USERS is None


class TestDynamicClaimsConfiguration:
    """Test per la configurazione dei claims dinamici"""

    def test_dynamic_claims_config_exists(self):
        """Verifica che DYNAMIC_CLAIMS_CONFIG esista"""
        assert DYNAMIC_CLAIMS_CONFIG is not None
        assert isinstance(DYNAMIC_CLAIMS_CONFIG, dict)

    def test_dynamic_claims_config_has_required_keys(self):
        """Verifica che DYNAMIC_CLAIMS_CONFIG abbia le chiavi necessarie"""
        required_keys = ["default_tenant_id", "default_roles", "default_groups"]

        for key in required_keys:
            assert key in DYNAMIC_CLAIMS_CONFIG

    def test_dynamic_claims_default_roles(self):
        """Verifica i ruoli di default"""
        assert isinstance(DYNAMIC_CLAIMS_CONFIG["default_roles"], list)
        assert len(DYNAMIC_CLAIMS_CONFIG["default_roles"]) > 0

    def test_dynamic_claims_default_groups(self):
        """Verifica i gruppi di default"""
        assert isinstance(DYNAMIC_CLAIMS_CONFIG["default_groups"], list)
        assert len(DYNAMIC_CLAIMS_CONFIG["default_groups"]) > 0

    def test_dynamic_claims_default_tenant_id(self):
        """Verifica il tenant ID di default"""
        assert isinstance(DYNAMIC_CLAIMS_CONFIG["default_tenant_id"], str)
        assert len(DYNAMIC_CLAIMS_CONFIG["default_tenant_id"]) > 0
