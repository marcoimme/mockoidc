#!/usr/bin/env python3
"""
Callback Server per test OIDC
Riceve l'authorization code e lo scambia con i token
"""

from flask import Flask, request, render_template_string
import requests
import json
from jose import jwt

app = Flask(__name__)

# Configurazione
MOCK_OIDC_URL = "http://localhost:8080"
CALLBACK_URL = "http://localhost:3000/callback"
CLIENT_ID = "demo-app"

# Template HTML per la pagina di callback
CALLBACK_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OIDC Callback - Token Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .content {
            padding: 30px;
        }

        .status {
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border-left: 4px solid #dc3545;
        }

        .status-icon {
            font-size: 2em;
        }

        .section {
            margin-bottom: 30px;
        }

        .section-title {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .token-box {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }

        .token-label {
            font-weight: 600;
            color: #495057;
            margin-bottom: 8px;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .token-value {
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            word-break: break-all;
            background: white;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #e9ecef;
            color: #212529;
            max-height: 150px;
            overflow-y: auto;
        }

        .claims-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .claim-item {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 12px;
        }

        .claim-key {
            font-weight: 600;
            color: #667eea;
            font-size: 0.9em;
            margin-bottom: 5px;
        }

        .claim-value {
            color: #495057;
            font-size: 0.95em;
            word-break: break-word;
        }

        .claim-value.array {
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: #e83e8c;
        }

        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            margin-right: 10px;
        }

        .btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }

        .btn-secondary {
            background: #6c757d;
        }

        .btn-secondary:hover {
            background: #5a6268;
        }

        .actions {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }

        .metadata {
            background: #e7f3ff;
            border-left: 4px solid #0066cc;
            padding: 15px;
            border-radius: 6px;
            margin-top: 15px;
        }

        .metadata-item {
            margin: 8px 0;
            font-size: 0.95em;
        }

        .metadata-label {
            font-weight: 600;
            color: #0066cc;
        }

        .code-highlight {
            background: #fff3cd;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .section {
            animation: slideIn 0.5s ease forwards;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 OIDC Token Viewer</h1>
            <p>Mock OIDC Server - Authorization Callback</p>
        </div>

        <div class="content">
            {% if error %}
            <div class="status error">
                <span class="status-icon">❌</span>
                <div>
                    <strong>Errore durante l'autenticazione</strong><br>
                    {{ error }}
                </div>
            </div>
            {% else %}
            <div class="status success">
                <span class="status-icon">✅</span>
                <div>
                    <strong>Autenticazione completata con successo!</strong><br>
                    Token ricevuti dal server OIDC
                </div>
            </div>

            <!-- Authorization Code -->
            <div class="section">
                <div class="section-title">
                    📝 Authorization Code
                </div>
                <div class="token-box">
                    <div class="token-label">Code</div>
                    <div class="token-value">{{ auth_code }}</div>
                </div>
                <div class="metadata">
                    <div class="metadata-item">
                        <span class="metadata-label">State:</span> {{ state or 'N/A' }}
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Redirect URI:</span> {{ callback_url }}
                    </div>
                </div>
            </div>

            <!-- Access Token -->
            <div class="section">
                <div class="section-title">
                    🎫 Access Token
                </div>
                <div class="token-box">
                    <div class="token-label">JWT Access Token</div>
                    <div class="token-value">{{ tokens.access_token }}</div>
                </div>
                <div class="metadata">
                    <div class="metadata-item">
                        <span class="metadata-label">Type:</span> {{ tokens.token_type }}
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Expires In:</span> {{ tokens.expires_in }} secondi
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Scope:</span> <span class="code-highlight">{{ tokens.scope }}</span>
                    </div>
                </div>
            </div>

            <!-- ID Token -->
            <div class="section">
                <div class="section-title">
                    🆔 ID Token
                </div>
                <div class="token-box">
                    <div class="token-label">JWT ID Token</div>
                    <div class="token-value">{{ tokens.id_token }}</div>
                </div>
            </div>

            <!-- ID Token Claims -->
            <div class="section">
                <div class="section-title">
                    📋 ID Token Claims (Azure AD Compatible)
                </div>
                <div class="claims-grid">
                    {% for key, value in id_token_claims.items() %}
                    <div class="claim-item">
                        <div class="claim-key">{{ key }}</div>
                        <div class="claim-value {% if value is iterable and value is not string %}array{% endif %}">
                            {% if value is iterable and value is not string %}
                                {{ value | tojson }}
                            {% else %}
                                {{ value }}
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Refresh Token -->
            <div class="section">
                <div class="section-title">
                    🔄 Refresh Token
                </div>
                <div class="token-box">
                    <div class="token-label">Refresh Token (Opaque)</div>
                    <div class="token-value">{{ tokens.refresh_token }}</div>
                </div>
            </div>

            <!-- Actions -->
            <div class="actions">
                <a href="/" class="btn">🔙 Torna all'inizio</a>
                <a href="{{ oidc_url }}" class="btn btn-secondary" target="_blank">📖 Discovery Endpoint</a>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OIDC Test Client</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 600px;
            width: 100%;
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .content {
            padding: 40px;
        }

        .info-box {
            background: #e7f3ff;
            border-left: 4px solid #0066cc;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }

        .info-box h3 {
            color: #0066cc;
            margin-bottom: 15px;
        }

        .info-item {
            margin: 10px 0;
            padding: 8px;
            background: white;
            border-radius: 4px;
        }

        .label {
            font-weight: 600;
            color: #495057;
            display: inline-block;
            width: 140px;
        }

        .value {
            color: #212529;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        .btn {
            display: block;
            width: 100%;
            padding: 15px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            text-align: center;
            font-size: 1.1em;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            margin-top: 20px;
        }

        .btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .users-box {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            border-radius: 6px;
            margin-top: 20px;
        }

        .users-box h4 {
            color: #856404;
            margin-bottom: 15px;
        }

        .user-item {
            background: white;
            padding: 10px;
            border-radius: 4px;
            margin: 8px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        .status {
            display: inline-block;
            padding: 4px 12px;
            background: #28a745;
            color: white;
            border-radius: 12px;
            font-size: 0.8em;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 OIDC Test Client</h1>
            <p>Mock OIDC Server Test Application</p>
        </div>

        <div class="content">
            <div class="info-box">
                <h3>📋 Configurazione</h3>
                <div class="info-item">
                    <span class="label">Server OIDC:</span>
                    <span class="value">{{ oidc_url }}</span>
                </div>
                <div class="info-item">
                    <span class="label">Client ID:</span>
                    <span class="value">{{ client_id }}</span>
                </div>
                <div class="info-item">
                    <span class="label">Redirect URI:</span>
                    <span class="value">{{ callback_url }}</span>
                </div>
                <div class="info-item">
                    <span class="label">Scopes:</span>
                    <span class="value">openid profile email</span>
                </div>
                <div class="info-item">
                    <span class="label">PKCE:</span>
                    <span class="value">S256</span>
                </div>
            </div>

            <a href="{{ auth_url }}" class="btn">
                🚀 Avvia Login OIDC
            </a>

            <div class="users-box">
                <h4>� Come Funziona</h4>
                <div class="user-item">
                    ✨ Usa <strong>qualsiasi email e password</strong>
                </div>
                <div class="user-item">
                    📧 I claims saranno generati dalla tua email
                </div>
                <div class="user-item">
                    🎯 Esempi: mario.rossi@company.com, test@example.com
                </div>
            </div>

            <span class="status">✓ Server Ready</span>
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def home():
    """Pagina iniziale con link per avviare il flusso OIDC"""
    import hashlib
    import base64
    import secrets

    # Genera PKCE
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("utf-8")
    challenge = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(challenge).rstrip(b"=").decode("utf-8")

    # Salva il verifier nella sessione (in produzione usare sessioni vere)
    # Per semplicità lo mettiamo in una variabile globale
    app.config["CODE_VERIFIER"] = code_verifier

    # Costruisci URL di autorizzazione
    from urllib.parse import urlencode

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": CALLBACK_URL,
        "scope": "openid profile email",
        "state": "demo-state-" + secrets.token_urlsafe(8),
        "nonce": "demo-nonce-" + secrets.token_urlsafe(8),
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = f"{MOCK_OIDC_URL}/authorize?{urlencode(params)}"

    return render_template_string(
        HOME_TEMPLATE, oidc_url=MOCK_OIDC_URL, client_id=CLIENT_ID, callback_url=CALLBACK_URL, auth_url=auth_url
    )


@app.route("/callback")
def callback():
    """Callback endpoint - riceve l'authorization code e lo scambia con i token"""

    # Ottieni parametri dalla query string
    code = request.args.get("code")
    state = request.args.get("state")
    error = request.args.get("error")

    if error:
        return render_template_string(
            CALLBACK_TEMPLATE, error=f"Errore OAuth: {error} - {request.args.get('error_description', 'N/A')}"
        )

    if not code:
        return render_template_string(CALLBACK_TEMPLATE, error="Authorization code mancante")

    try:
        # Recupera il code_verifier
        code_verifier = app.config.get("CODE_VERIFIER")

        # Scambia il code con i token
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": CALLBACK_URL,
            "client_id": CLIENT_ID,
            "code_verifier": code_verifier,
        }

        response = requests.post(f"{MOCK_OIDC_URL}/token", data=token_data)

        if response.status_code != 200:
            return render_template_string(
                CALLBACK_TEMPLATE, error=f"Errore token exchange: {response.status_code} - {response.text}"
            )

        tokens = response.json()

        # Decodifica l'ID token
        id_token_claims = jwt.get_unverified_claims(tokens["id_token"])

        return render_template_string(
            CALLBACK_TEMPLATE,
            auth_code=code,
            state=state,
            tokens=tokens,
            id_token_claims=id_token_claims,
            callback_url=CALLBACK_URL,
            oidc_url=f"{MOCK_OIDC_URL}/.well-known/openid-configuration",
        )

    except Exception as e:
        return render_template_string(CALLBACK_TEMPLATE, error=f"Errore durante il processamento: {str(e)}")


if __name__ == "__main__":
    print("=" * 70)
    print("🌐 OIDC Callback Server")
    print("=" * 70)
    print()
    print(f"✅ Server avviato su: http://localhost:3000")
    print(f"✅ Callback URL: {CALLBACK_URL}")
    print(f"✅ OIDC Server: {MOCK_OIDC_URL}")
    print()
    print("📝 Apri http://localhost:3000 nel browser per iniziare")
    print()
    print("=" * 70)

    app.run(host="0.0.0.0", port=3000, debug=True)
