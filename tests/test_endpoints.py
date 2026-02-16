"""
Unit tests per gli endpoint principali del Mock OIDC Server
"""


class TestDiscoveryEndpoint:
    """Test per il discovery endpoint"""

    def test_discovery_endpoint_returns_200(self, test_client):
        """Verifica che il discovery endpoint restituisca 200"""
        response = test_client.get("/.well-known/openid-configuration")
        assert response.status_code == 200

    def test_discovery_endpoint_returns_valid_json(self, test_client):
        """Verifica che il discovery endpoint restituisca JSON valido"""
        response = test_client.get("/.well-known/openid-configuration")
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)

    def test_discovery_endpoint_contains_required_fields(self, test_client):
        """Verifica che il discovery endpoint contenga i campi obbligatori"""
        response = test_client.get("/.well-known/openid-configuration")
        data = response.json()

        required_fields = ["issuer", "authorization_endpoint", "token_endpoint", "userinfo_endpoint", "jwks_uri"]

        for field in required_fields:
            assert field in data, f"Campo obbligatorio '{field}' mancante"

    def test_discovery_endpoint_has_correct_scopes(self, test_client):
        """Verifica che gli scopes supportati siano corretti"""
        response = test_client.get("/.well-known/openid-configuration")
        data = response.json()

        assert "scopes_supported" in data
        assert "openid" in data["scopes_supported"]
        assert "profile" in data["scopes_supported"]
        assert "email" in data["scopes_supported"]

    def test_discovery_endpoint_dynamic_issuer(self, test_client):
        """Verifica che l'issuer sia dinamico basato sulla richiesta"""
        response = test_client.get("/.well-known/openid-configuration")
        data = response.json()

        # L'issuer dovrebbe corrispondere al base URL della richiesta
        assert "issuer" in data
        assert data["issuer"].startswith("http://")


class TestJWKSEndpoint:
    """Test per il JWKS endpoint"""

    def test_jwks_endpoint_returns_200(self, test_client):
        """Verifica che il JWKS endpoint restituisca 200"""
        response = test_client.get("/jwks")
        assert response.status_code == 200

    def test_jwks_endpoint_returns_valid_structure(self, test_client):
        """Verifica che il JWKS endpoint restituisca una struttura valida"""
        response = test_client.get("/jwks")
        data = response.json()

        assert "keys" in data
        assert isinstance(data["keys"], list)
        assert len(data["keys"]) > 0

    def test_jwks_keys_have_required_fields(self, test_client):
        """Verifica che le chiavi JWKS abbiano i campi obbligatori"""
        response = test_client.get("/jwks")
        data = response.json()

        key = data["keys"][0]
        required_fields = ["kty", "use", "kid", "n", "e", "alg"]

        for field in required_fields:
            assert field in key, f"Campo obbligatorio '{field}' mancante nella chiave"

    def test_jwks_key_type_is_rsa(self, test_client):
        """Verifica che il tipo di chiave sia RSA"""
        response = test_client.get("/jwks")
        data = response.json()

        key = data["keys"][0]
        assert key["kty"] == "RSA"
        assert key["alg"] == "RS256"
        assert key["use"] == "sig"


class TestAuthorizationEndpoint:
    """Test per l'authorization endpoint"""

    def test_authorize_without_credentials_shows_login_form(self, test_client, auth_params):
        """Verifica che senza credenziali venga mostrato il form di login"""
        response = test_client.get("/authorize", params=auth_params)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert b"login" in response.content.lower()

    def test_authorize_with_invalid_response_type_returns_400(self, test_client):
        """Verifica che un response_type non valido restituisca 400"""
        params = {
            "response_type": "invalid",
            "client_id": "test-client",
            "redirect_uri": "http://localhost:3000/callback",
        }
        response = test_client.get("/authorize", params=params)
        assert response.status_code == 400

    def test_authorize_with_credentials_redirects(self, test_client, auth_params):
        """Verifica che con credenziali valide ci sia un redirect"""
        params = {**auth_params, "username": "test@example.com", "password": "test123"}
        response = test_client.get("/authorize", params=params, follow_redirects=False)

        # Dovrebbe essere un redirect (307)
        assert response.status_code in [302, 303, 307]
        assert "location" in response.headers

    def test_authorize_redirect_contains_code_and_state(self, test_client, auth_params):
        """Verifica che il redirect contenga code e state"""
        params = {**auth_params, "username": "test@example.com", "password": "test123"}
        response = test_client.get("/authorize", params=params, follow_redirects=False)

        location = response.headers.get("location", "")
        assert "code=" in location
        assert "state=" in location
        assert auth_params["state"] in location


class TestTokenEndpoint:
    """Test per il token endpoint"""

    def test_token_endpoint_requires_grant_type(self, test_client):
        """Verifica che il token endpoint richieda grant_type"""
        response = test_client.post("/token", data={})
        assert response.status_code == 422  # Validation error

    def test_token_endpoint_with_invalid_code_returns_400(self, test_client):
        """Verifica che un code non valido restituisca 400"""
        data = {
            "grant_type": "authorization_code",
            "code": "invalid-code",
            "redirect_uri": "http://localhost:3000/callback",
            "client_id": "test-client",
        }
        response = test_client.post("/token", data=data)
        assert response.status_code == 400

    def test_token_endpoint_full_flow(self, test_client, auth_params):
        """Test del flusso completo: authorize -> token"""
        # 1. Ottieni authorization code
        params = {**auth_params, "username": "test@example.com", "password": "test123"}
        auth_response = test_client.get("/authorize", params=params, follow_redirects=False)

        # Estrai il code dalla location
        location = auth_response.headers.get("location", "")
        code = location.split("code=")[1].split("&")[0]

        # 2. Scambia il code con i token
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": auth_params["redirect_uri"],
            "client_id": auth_params["client_id"],
        }
        token_response = test_client.post("/token", data=token_data)

        assert token_response.status_code == 200
        tokens = token_response.json()

        # Verifica struttura response
        assert "access_token" in tokens
        assert "token_type" in tokens
        assert "expires_in" in tokens
        assert "id_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "Bearer"


class TestUserInfoEndpoint:
    """Test per il userinfo endpoint"""

    def test_userinfo_without_token_returns_401(self, test_client):
        """Verifica che senza token restituisca 401"""
        response = test_client.get("/userinfo")
        assert response.status_code == 401

    def test_userinfo_with_invalid_token_returns_401(self, test_client):
        """Verifica che con token non valido restituisca 401"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = test_client.get("/userinfo", headers=headers)
        assert response.status_code == 401

    def test_userinfo_full_flow(self, test_client, auth_params):
        """Test del flusso completo per userinfo"""
        # 1. Ottieni authorization code
        params = {**auth_params, "username": "mario.rossi@example.com", "password": "test123"}
        auth_response = test_client.get("/authorize", params=params, follow_redirects=False)
        location = auth_response.headers.get("location", "")
        code = location.split("code=")[1].split("&")[0]

        # 2. Ottieni access token
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": auth_params["redirect_uri"],
            "client_id": auth_params["client_id"],
        }
        token_response = test_client.post("/token", data=token_data)
        tokens = token_response.json()
        access_token = tokens["access_token"]

        # 3. Usa access token per userinfo
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = test_client.get("/userinfo", headers=headers)

        assert userinfo_response.status_code == 200
        userinfo = userinfo_response.json()

        # Verifica campi obbligatori
        assert "sub" in userinfo
        assert "email" in userinfo
        assert "name" in userinfo


class TestHealthEndpoint:
    """Test per gli endpoint di health check"""

    def test_health_endpoint_returns_200(self, test_client):
        """Verifica che l'endpoint health restituisca 200"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint_returns_info(self, test_client):
        """Verifica che il root endpoint restituisca informazioni sul server"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
