# Mock OIDC Server

Un'implementazione Python di un server mock OpenID Connect (OIDC) per testing e sviluppo, costruito con FastAPI.

## Caratteristiche

- **Endpoint OIDC Standard**:
  - Discovery (`.well-known/openid-configuration`) con **URL dinamici**
  - Authorization (`/authorize`)
  - Token (`/token`)
  - UserInfo (`/userinfo`)
  - JWKS (`/jwks`)
  - Revoke (`/revoke`)
  - Logout (`/logout`)

- **Sicurezza**:
  - JWT firmati con RS256
  - Supporto PKCE (Proof Key for Code Exchange)
  - Authorization Code Flow
  - Refresh Token Flow

- **Utenti Mock**:
  - Utenti configurabili con claims personalizzati
  - Claims compatibili con Azure AD (oid, tid, upn, roles, groups)
  - Form di login interattivo

- **Configurazione**:
  - Configurabile via variabili d'ambiente
  - Storage in-memory per codes e tokens
  - Logging dettagliato

- **Deploy**:
  - Docker & Docker Compose ready
  - Helm chart per Kubernetes
  - Supporto per HA e autoscaling

## 📦 Installazione

### Prerequisiti

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) (gestore pacchetti Python veloce)

### Installazione di uv

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Oppure tramite pip
pip install uv
```

### Setup

1. **Clona il repository** (o crea la directory):
```bash
cd mockoidc
```

2. **Crea un virtual environment e installa le dipendenze**:
```bash
# uv crea automaticamente il venv e installa tutto
uv sync

# Oppure manualmente
uv venv
source .venv/bin/activate  # Su Linux/Mac
# oppure
.venv\Scripts\activate  # Su Windows
uv pip install -e .
```

4. **Configura l'ambiente** (opzionale):
```bash
cp .env.example .env
# Modifica .env secondo le tue necessità
```

## 🚀 Avvio

### Modo 1: Test Visuale con UI Web (Consigliato ⭐)

Il modo più semplice per testare l'intero flusso:

**Terminale 1 - Server OIDC:**
```bash
uv run python main.py
# Server OIDC disponibile su http://localhost:8080
```

**Terminale 2 - Server Callback Demo:**
```bash
uv run python demo/callback_server.py
# UI demo disponibile su http://localhost:3000
```

Poi apri il browser su **http://localhost:3000** e segui il flusso interattivo!

Vedrai:
- 📝 Form di login con UI professionale
- 🎫 Authorization code generato
- 🔐 Access token, ID token e Refresh token
- 📋 Tutti i claims decodificati (oid, tid, upn, roles, groups)
- ✨ UI moderna e responsive

### Modo 2: Solo Server OIDC

Se vuoi solo il server mock senza la UI di test:

```bash
# Usando Python direttamente
uv run python main.py
```

Oppure:

```bash
# Usando Uvicorn
uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Il server sarà disponibile su `http://localhost:8080`

## � Demo - Come funziona

### Demo Completa con UI Interattiva

La demo include due componenti:

1. **Mock OIDC Server** (porta 8080) - Simula un provider OIDC come Azure AD
2. **Callback Demo Server** (porta 3000) - Simula la tua applicazione client

#### Avvio dell'ambiente demo

**Passo 1: Avvia il server OIDC**
```bash
# Terminale 1
uv run python main.py
```

Output atteso:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete.
```

**Passo 2: Avvia il server callback demo**
```bash
# Terminale 2 (in una nuova finestra)
uv run python demo/callback_server.py
```

Output atteso:
```
 * Running on http://0.0.0.0:3000
 * Press CTRL+C to quit
```

#### Flusso della demo

**1. Apri la home page della demo**
```
http://localhost:3000
```

Vedrai un pulsante "Avvia Login OIDC" con informazioni sul flusso.

**2. Clicca su "Avvia Login OIDC"**

Vieni reindirizzato al server OIDC:
```
http://localhost:8080/authorize?response_type=code&client_id=demo-app&redirect_uri=http://localhost:3000/callback&scope=openid+profile+email&state=xyz789
```

**3. Inserisci le credenziali di test**

Form di login con utenti pre-configurati:
- 👤 **User 1**: `user1@example.com` / `password1`
  - Role: User
  - Groups: developers, users
  
- 👨‍💼 **Admin**: `admin@example.com` / `admin123`
  - Role: Admin
  - Groups: admins, managers

**4. Autorizza l'applicazione**

Dopo il login, vieni reindirizzato al callback con l'authorization code:
```
http://localhost:3000/callback?code=abc123xyz&state=xyz789
```

**5. Visualizza i token**

La pagina di callback mostra:

✅ **Authorization Code**
```
abc123xyz
```

✅ **Access Token** (JWT decodificato)
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

✅ **ID Token** (JWT decodificato)
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

**6. Testa il refresh token**

Puoi usare il refresh token per ottenere nuovi access token:
```bash
curl -X POST http://localhost:8080/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=refresh_abc123xyz"
```

### Test rapido senza UI

Se preferisci testare via API senza l'interfaccia web:

```bash
# 1. Ottieni la configurazione OIDC
curl http://localhost:8080/.well-known/openid-configuration | jq

# 2. Ottieni le chiavi pubbliche
curl http://localhost:8080/jwks | jq

# 3. Apri nel browser per il login
open "http://localhost:8080/authorize?response_type=code&client_id=test&redirect_uri=http://localhost:3000/callback&scope=openid%20profile%20email&state=test123"

# 4. Dopo il login, copia il code dall'URL e scambialo con i token
curl -X POST http://localhost:8080/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=IL_TUO_CODE" \
  -d "redirect_uri=http://localhost:3000/callback" \
  -d "client_id=test" | jq

# 5. Usa l'access token per ottenere info utente
curl http://localhost:8080/userinfo \
  -H "Authorization: Bearer IL_TUO_ACCESS_TOKEN" | jq
```

## �🌐 Discovery con URL Dinamici

Una caratteristica importante: il Mock OIDC Server adatta **automaticamente** gli URL nella risposta discovery (`.well-known/openid-configuration`) e **l'issuer nei token JWT** in base all'host:port della richiesta HTTP.

**Esempi**:
```bash
# Chiamata con localhost
curl http://localhost:8080/.well-known/openid-configuration
# → issuer: "http://localhost:8080"
# → authorization_endpoint: "http://localhost:8080/authorize"

# I token JWT generati avranno:
# access_token: { "iss": "http://localhost:8080", ... }
# id_token: { "iss": "http://localhost:8080", ... }

# Chiamata con IP
curl http://127.0.0.1:8080/.well-known/openid-configuration  
# → issuer: "http://127.0.0.1:8080"
# → I token avranno: "iss": "http://127.0.0.1:8080"

# In Kubernetes
curl http://mockoidc.default.svc.cluster.local:8080/.well-known/openid-configuration
# → issuer: "http://mockoidc.default.svc.cluster.local:8080"
# → I token avranno lo stesso issuer
```

**Vantaggi**:
- ✅ Funziona in locale, Docker, Kubernetes senza modificare configurazione
- ✅ Gli applicativi client ricevono sempre gli URL corretti
- ✅ **I token JWT hanno sempre l'issuer corretto** per l'ambiente
- ✅ Validazione dell'issuer sempre consistente
- ✅ Nessuna necessità di configurare `ISSUER` manualmente

## 📖 Utilizzo



## 🔍 API Documentation

FastAPI genera automaticamente la documentazione interattiva:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## ☸️ Deploy su Kubernetes

Il progetto include un chart Helm completo per il deployment su cluster Kubernetes.

### Quick Start Kubernetes

```bash
# 1. Build dell'immagine Docker
docker build -t mockoidc:1.0.0 .

# 2. Deploy con Helm (ambiente dev)
helm install mockoidc .helm/ -f .helm/values-dev.yaml

# 3. Port-forward per accesso locale
kubectl port-forward svc/mockoidc 8080:8080

# 4. Test
curl http://localhost:8080/health
```

### Deploy in Produzione

```bash
# Con ingress e TLS
helm install mockoidc .helm/ -f .helm/values-prod.yaml

# Con autoscaling abilitato
helm install mockoidc .helm/ \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=10
```

### Gestione

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

## ⚠️ Note di Sicurezza

**ATTENZIONE**: Questo è un server MOCK per testing/sviluppo.

❌ **NON usare in produzione**
- Storage in-memory (dati persi al restart)
- Nessuna validazione robusta client_id/secret
- Chiavi RSA generate dinamicamente

## 🤝 Contributi

I contributi sono benvenuti! Apri una issue o una pull request.

## 📞 Supporto

Per problemi o domande, apri una issue su GitHub.
