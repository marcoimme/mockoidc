import logging
from typing import Dict, Optional

from fastapi import FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from claims_generator import generate_claims_from_email
from config import MOCK_USERS, settings
from jwks_service import jwks_service
from models import AuthorizationCode, DiscoveryResponse, JWKSResponse, TokenResponse, UserInfoResponse
from token_service import token_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crea l'app FastAPI
app = FastAPI(title="Mock OIDC Server", description="Mock OpenID Connect Provider for testing", version="1.0.0")

# Storage in-memory per authorization codes, tokens e sessioni
authorization_codes: Dict[str, AuthorizationCode] = {}
refresh_tokens: Dict[str, dict] = {}
revoked_tokens: set = set()


@app.get("/.well-known/openid-configuration", response_model=DiscoveryResponse)
async def discovery(request: Request):
    """Discovery endpoint - restituisce la configurazione OIDC"""
    # Costruisce il base_url dinamicamente dalla richiesta
    base_url = str(request.base_url).rstrip("/")

    logger.info(f"Discovery endpoint called - base_url: {base_url}")

    return DiscoveryResponse(
        issuer=base_url,
        authorization_endpoint=f"{base_url}/authorize",
        token_endpoint=f"{base_url}/token",
        userinfo_endpoint=f"{base_url}/userinfo",
        jwks_uri=f"{base_url}/jwks",
        revocation_endpoint=f"{base_url}/revoke",
        end_session_endpoint=f"{base_url}/logout",
        response_types_supported=settings.supported_response_types,
        scopes_supported=settings.supported_scopes,
    )


@app.get("/authorize")
async def authorize(
    response_type: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(default="openid"),
    state: Optional[str] = Query(default=None),
    nonce: Optional[str] = Query(default=None),
    code_challenge: Optional[str] = Query(default=None),
    code_challenge_method: Optional[str] = Query(default=None),
    username: Optional[str] = Query(default=None),
    password: Optional[str] = Query(default=None),
):
    """Authorization endpoint - gestisce il flusso di autorizzazione"""
    logger.info(f"Authorization endpoint called - client_id: {client_id}, response_type: {response_type}")

    # Valida response_type
    if response_type not in settings.supported_response_types:
        raise HTTPException(status_code=400, detail="Unsupported response_type")

    # Se non ci sono credenziali, mostra form di login
    if not username or not password:
        return HTMLResponse(
            content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mock OIDC - Login</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 400px; margin: 100px auto; padding: 20px; }}
                input {{ width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }}
            button {{ width: 100%; padding: 10px; background: #0066cc; color: white; border: none; cursor: pointer; }}
                button:hover {{ background: #0052a3; }}
                .info {{ background: #f0f0f0; padding: 10px; margin: 20px 0; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h2>Mock OIDC Login</h2>
            <div class="info">
                <strong>Client ID:</strong> {client_id}<br>
                <strong>Scopes:</strong> {scope}
            </div>
            <form method="get">
                <input type="hidden" name="response_type" value="{response_type}">
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                <input type="hidden" name="scope" value="{scope}">
                <input type="hidden" name="state" value="{state or ""}">
                <input type="hidden" name="nonce" value="{nonce or ""}">
                <input type="hidden" name="code_challenge" value="{code_challenge or ""}">
                <input type="hidden" name="code_challenge_method" value="{code_challenge_method or ""}">

                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>

            <div class="info">
                <strong>💡 Suggerimento:</strong><br>
                Puoi usare <strong>qualsiasi email e password</strong>!<br>
                I claims saranno generati automaticamente dalla tua email.<br><br>
                <em>Esempi: mario.rossi@company.com, test@example.com</em>
            </div>
        </body>
        </html>
        """
        )

    # Autentica l'utente
    user = None

    # Se MOCK_USERS è configurato, cerca l'utente nella lista
    if MOCK_USERS is not None:
        for mock_user in MOCK_USERS:
            if mock_user["username"] == username and mock_user["password"] == password:
                user = mock_user
                break

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        # Modalità dinamica: accetta qualsiasi email/password
        # Valida che l'username sia una email valida
        if not username or "@" not in username:
            raise HTTPException(status_code=400, detail="Username must be a valid email address")

        # Genera claims dinamicamente dalla email
        logger.info(f"Generating dynamic claims for email: {username}")
        user_claims = generate_claims_from_email(username)

        user = {
            "username": username,
            "password": password,  # Non viene validata in modalità dinamica
            "claims": user_claims,
        }

    # Gestisce il flusso authorization code
    if "code" in response_type:
        # Genera authorization code
        code = token_service.generate_authorization_code()

        # Salva il code con i dati associati
        authorization_codes[code] = AuthorizationCode(
            code=code,
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            user_claims=user["claims"],
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            nonce=nonce,
        )

        # Costruisci URL di redirect
        redirect_params = f"code={code}"
        if state:
            redirect_params += f"&state={state}"

        redirect_url = f"{redirect_uri}?{redirect_params}"
        logger.info(f"Redirecting to: {redirect_url}")

        return RedirectResponse(url=redirect_url)

    raise HTTPException(status_code=400, detail="Unsupported response_type")


@app.post("/token", response_model=TokenResponse)
async def token(
    request: Request,
    grant_type: str = Form(...),
    code: Optional[str] = Form(default=None),
    redirect_uri: Optional[str] = Form(default=None),
    client_id: Optional[str] = Form(default=None),
    client_secret: Optional[str] = Form(default=None),
    code_verifier: Optional[str] = Form(default=None),
    refresh_token: Optional[str] = Form(default=None),
):
    """Token endpoint - scambia authorization code con access token"""
    logger.info(f"Token endpoint called - grant_type: {grant_type}")

    if grant_type == "authorization_code":
        if not code:
            raise HTTPException(status_code=400, detail="Missing code parameter")

        # Recupera l'authorization code
        auth_code = authorization_codes.get(code)
        if not auth_code:
            raise HTTPException(status_code=400, detail="Invalid authorization code")

        # Valida redirect_uri
        if redirect_uri != auth_code.redirect_uri:
            raise HTTPException(status_code=400, detail="Invalid redirect_uri")

        # Valida PKCE se presente
        if auth_code.code_challenge:
            if not code_verifier:
                raise HTTPException(status_code=400, detail="Missing code_verifier")

            if not token_service.validate_pkce(
                code_verifier, auth_code.code_challenge, auth_code.code_challenge_method
            ):
                raise HTTPException(status_code=400, detail="Invalid code_verifier")

        # Ricava l'issuer dinamicamente dalla richiesta
        base_url = str(request.base_url).rstrip("/")

        # Genera i token con issuer dinamico
        access_token = token_service.generate_access_token(auth_code.user_claims, auth_code.scope, issuer=base_url)

        id_token = token_service.generate_id_token(
            auth_code.user_claims, auth_code.client_id, auth_code.nonce, issuer=base_url
        )

        refresh_token_value = token_service.generate_refresh_token()

        # Salva il refresh token
        refresh_tokens[refresh_token_value] = {
            "user_claims": auth_code.user_claims,
            "scope": auth_code.scope,
            "client_id": auth_code.client_id,
        }

        # Elimina il code (può essere usato una sola volta)
        del authorization_codes[code]

        logger.info("Tokens generated successfully")

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.access_token_expiry,
            id_token=id_token,
            refresh_token=refresh_token_value,
            scope=auth_code.scope,
        )

    elif grant_type == "refresh_token":
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Missing refresh_token parameter")

        # Recupera il refresh token
        rt_data = refresh_tokens.get(refresh_token)
        if not rt_data:
            raise HTTPException(status_code=400, detail="Invalid refresh token")

        # Ricava l'issuer dinamicamente dalla richiesta
        base_url = str(request.base_url).rstrip("/")

        # Genera nuovi token con issuer dinamico
        access_token = token_service.generate_access_token(rt_data["user_claims"], rt_data["scope"], issuer=base_url)

        id_token = token_service.generate_id_token(rt_data["user_claims"], rt_data["client_id"], issuer=base_url)

        logger.info("Tokens refreshed successfully")

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=settings.access_token_expiry,
            id_token=id_token,
            scope=rt_data["scope"],
        )

    else:
        raise HTTPException(status_code=400, detail="Unsupported grant_type")


@app.get("/userinfo", response_model=UserInfoResponse)
async def userinfo(request: Request):
    """UserInfo endpoint - restituisce i dati dell'utente autenticato"""
    logger.info("UserInfo endpoint called")

    # Estrai il token dall'header Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.replace("Bearer ", "")

    # Verifica che il token non sia revocato
    if token in revoked_tokens:
        raise HTTPException(status_code=401, detail="Token has been revoked")

    try:
        # Decodifica il token
        claims = token_service.decode_token(token)

        # Restituisci le informazioni dell'utente
        return UserInfoResponse(
            sub=claims.get("sub"),
            name=claims.get("name"),
            given_name=claims.get("given_name"),
            family_name=claims.get("family_name"),
            email=claims.get("email"),
            oid=claims.get("oid"),
            tid=claims.get("tid"),
            upn=claims.get("upn"),
            preferred_username=claims.get("preferred_username"),
            roles=claims.get("roles"),
            groups=claims.get("groups"),
        )
    except Exception as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token") from e


@app.get("/jwks", response_model=JWKSResponse)
async def jwks():
    """JWKS endpoint - restituisce le chiavi pubbliche per validare i token"""
    logger.info("JWKS endpoint called")
    return jwks_service.get_jwks()


@app.post("/revoke")
async def revoke(token: str = Form(...), token_type_hint: Optional[str] = Form(default=None)):
    """Revoke endpoint - revoca un token"""
    logger.info(f"Revoke endpoint called - token_type_hint: {token_type_hint}")

    # Aggiungi il token alla lista dei revocati
    revoked_tokens.add(token)

    # Se è un refresh token, rimuovilo dallo storage
    if token in refresh_tokens:
        del refresh_tokens[token]

    return JSONResponse(content={"message": "Token revoked successfully"})


@app.get("/logout")
async def logout(
    post_logout_redirect_uri: Optional[str] = Query(default=None), state: Optional[str] = Query(default=None)
):
    """Logout endpoint"""
    logger.info("Logout endpoint called")

    if post_logout_redirect_uri:
        redirect_url = post_logout_redirect_uri
        if state:
            redirect_url += f"?state={state}"
        return RedirectResponse(url=redirect_url)

    return JSONResponse(content={"message": "Logged out successfully"})


@app.get("/")
async def root(request: Request):
    """Root endpoint con informazioni sul server"""
    base_url = str(request.base_url).rstrip("/")
    return {
        "name": "Mock OIDC Server",
        "version": "1.0.0",
        "discovery": f"{base_url}/.well-known/openid-configuration",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
