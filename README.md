# Mock OIDC Server

A Python implementation of a mock OpenID Connect (OIDC) server for testing and development, built with FastAPI.

## Features

- **Standard OIDC Endpoints**:
  - Discovery (`.well-known/openid-configuration`) with **dynamic URLs**
  - Authorization (`/authorize`)
  - Token (`/token`)
  - UserInfo (`/userinfo`)
  - JWKS (`/jwks`)
  - Revoke (`/revoke`)
  - Logout (`/logout`)

- **Security**:
  - JWT signed with RS256
  - PKCE (Proof Key for Code Exchange) support
  - Authorization Code Flow
  - Refresh Token Flow

- **Mock Users**:
  - Configurable users with custom claims
  - Azure AD compatible claims (oid, tid, upn, roles, groups)
  - Interactive login form

- **Configuration**:
  - Configurable via environment variables
  - In-memory storage for codes and tokens
  - Detailed logging

- **Deployment**:
  - Docker & Docker Compose ready
  - Helm chart for Kubernetes
  - HA and autoscaling support

## 📦 Installation

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)

### Installing uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

### Setup

1. **Clone the repository** (or create the directory):
```bash
cd mockoidc
```

2. **Create a virtual environment and install dependencies**:
```bash
# uv automatically creates the venv and installs everything
uv sync

# Or manually
uv venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
uv pip install -e .
```

3. **Configure the environment** (optional):
```bash
cp .env.example .env
# Edit .env as needed
```

## 🚀 Getting Started

### Method 1: Visual Test with Web UI (Recommended ⭐)

The easiest way to test the entire flow:

**Terminal 1 - OIDC Server:**
```bash
uv run python main.py
# OIDC server available at http://localhost:8080
```

**Terminal 2 - Demo Callback Server:**
```bash
uv run python demo/callback_server.py
# Demo UI available at http://localhost:3000
```

Then open your browser at **http://localhost:3000** and follow the interactive flow!

You'll see:
- 📝 Login form with professional UI
- 🎫 Generated authorization code
- 🔐 Access token, ID token and Refresh token
- 📋 All decoded claims (oid, tid, upn, roles, groups)
- ✨ Modern and responsive UI

### Method 2: OIDC Server Only

If you just want the mock server without the test UI:

```bash
# Using Python directly
uv run python main.py
```

Or:

```bash
# Using Uvicorn
uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

The server will be available at `http://localhost:8080`

## 🎯 Demo - How it Works

### Complete Demo with Interactive UI

The demo includes two components:

1. **Mock OIDC Server** (port 8080) - Simulates an OIDC provider like Azure AD
2. **Callback Demo Server** (port 3000) - Simulates your client application

#### Starting the Demo Environment

**Step 1: Start the OIDC server**
```bash
# Terminal 1
uv run python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete.
```

**Step 2: Start the demo callback server**
```bash
# Terminal 2 (in a new window)
uv run python demo/callback_server.py
```

Expected output:
```
 * Running on http://0.0.0.0:3000
 * Press CTRL+C to quit
```

#### Demo Flow

**1. Open the demo home page**
```
http://localhost:3000
```

You'll see a "Start OIDC Login" button with flow information.

**2. Click on "Start OIDC Login"**

You'll be redirected to the OIDC server:
```
http://localhost:8080/authorize?response_type=code&client_id=demo-app&redirect_uri=http://localhost:3000/callback&scope=openid+profile+email&state=xyz789
```

**3. Enter test credentials**

Login form with pre-configured users:
- 👤 **User 1**: `user1@example.com` / `password1`
  - Role: User
  - Groups: developers, users

- 👨‍💼 **Admin**: `admin@example.com` / `admin123`
  - Role: Admin
  - Groups: admins, managers

**4. Authorize the application**

After login, you'll be redirected to the callback with the authorization code:
```
http://localhost:3000/callback?code=abc123xyz&state=xyz789
```

**5. View the tokens**

The callback page shows:

✅ **Authorization Code**
```
abc123xyz
```

✅ **Access Token** (decoded JWT)
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "oid": "550e8400-e29b-41d4-a716-446655440000",
  "tid": "9188040d-6c67-4c5b-b112-36a304b66dad",
  "upn": "user1@example.com",
  "name": "Mario Rossi",
  "roles": ["User"],
  "groups": ["developers", "users"],
  "iss": "http://localhost:8080",
  "aud": "demo-app",
  "exp": 1708123456
}
```

✅ **ID Token** (decoded JWT)
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user1@example.com",
  "email_verified": true,
  "name": "Mario Rossi",
  "given_name": "Mario",
  "family_name": "Rossi",
  "iss": "http://localhost:8080",
  "aud": "demo-app"
}
```

✅ **Refresh Token**
```
refresh_abc123xyz
```

**6. Test the refresh token**

You can use the refresh token to obtain new access tokens:
```bash
curl -X POST http://localhost:8080/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=refresh_abc123xyz"
```

### Quick Test Without UI

If you prefer to test via API without the web interface:

```bash
# 1. Get the OIDC configuration
curl http://localhost:8080/.well-known/openid-configuration | jq

# 2. Get the public keys
curl http://localhost:8080/jwks | jq

# 3. Open in browser for login
open "http://localhost:8080/authorize?response_type=code&client_id=test&redirect_uri=http://localhost:3000/callback&scope=openid%20profile%20email&state=test123"

# 4. After login, copy the code from the URL and exchange it for tokens
curl -X POST http://localhost:8080/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_CODE" \
  -d "redirect_uri=http://localhost:3000/callback" \
  -d "client_id=test" | jq

# 5. Use the access token to get user info
curl http://localhost:8080/userinfo \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" | jq
```

## 🌐 Discovery with Dynamic URLs

An important feature: The Mock OIDC Server **automatically adapts** the URLs in the discovery response (`.well-known/openid-configuration`) and **the issuer in JWT tokens** based on the host:port of the HTTP request.

**Examples**:
```bash
# Request with localhost
curl http://localhost:8080/.well-known/openid-configuration
# → issuer: "http://localhost:8080"
# → authorization_endpoint: "http://localhost:8080/authorize"

# Generated JWT tokens will have:
# access_token: { "iss": "http://localhost:8080", ... }
# id_token: { "iss": "http://localhost:8080", ... }

# Request with IP
curl http://127.0.0.1:8080/.well-known/openid-configuration  
# → issuer: "http://127.0.0.1:8080"
# → Tokens will have: "iss": "http://127.0.0.1:8080"

# In Kubernetes
curl http://mockoidc.default.svc.cluster.local:8080/.well-known/openid-configuration
# → issuer: "http://mockoidc.default.svc.cluster.local:8080"
# → Tokens will have the same issuer
```

**Benefits**:
- ✅ Works locally, in Docker, Kubernetes without changing configuration
- ✅ Client applications always receive the correct URLs
- ✅ **JWT tokens always have the correct issuer** for the environment
- ✅ Issuer validation always consistent
- ✅ No need to manually configure `ISSUER`

## 📖 Usage

## 🔍 API Documentation

FastAPI automatically generates interactive documentation:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## ☸️ Deploy to Kubernetes

The project includes a complete Helm chart for deployment to Kubernetes clusters.

### Kubernetes Quick Start

```bash
# 1. Build the Docker image
docker build -t mockoidc:1.0.0 .

# 2. Deploy with Helm (dev environment)
helm install mockoidc .helm/ -f .helm/values-dev.yaml

# 3. Port-forward for local access
kubectl port-forward svc/mockoidc 8080:8080

# 4. Test
curl http://localhost:8080/health
```

### Production Deployment

```bash
# With ingress and TLS
helm install mockoidc .helm/ -f .helm/values-prod.yaml

# With autoscaling enabled
helm install mockoidc .helm/ \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=10
```

### Management

```bash
# Upgrade
helm upgrade mockoidc .helm/ -f .helm/values-prod.yaml

# Status
helm status mockoidc

# Logs
kubectl logs -l app.kubernetes.io/name=mockoidc -f

# Uninstall
helm uninstall mockoidc
```

## ⚠️ Security Notes

**WARNING**: This is a MOCK server for testing/development.

❌ **DO NOT use in production**
- In-memory storage (data lost on restart)
- No robust client_id/secret validation
- Dynamically generated RSA keys

## 🤝 Contributing

Contributions are welcome! Open an issue or pull request.

## 📞 Support

For issues or questions, open an issue on GitHub.
