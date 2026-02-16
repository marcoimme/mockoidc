# Mock OIDC Server - Test Suite

Suite completa di unit test per il Mock OIDC Server.

## 📦 Installazione Dipendenze Test

```bash
# Installa dipendenze inclusi i test
uv sync

# Oppure installa solo le dipendenze dev
uv pip install -e ".[dev]"
```

## 🚀 Esecuzione Test

### Esegui tutti i test

```bash
# Con uv
uv run pytest

# Con pytest direttamente (se nell'ambiente virtuale)
pytest
```

### Esegui test specifici

```bash
# Test di un singolo file
uv run pytest tests/test_endpoints.py

# Test di una singola classe
uv run pytest tests/test_endpoints.py::TestDiscoveryEndpoint

# Test di un singolo metodo
uv run pytest tests/test_endpoints.py::TestDiscoveryEndpoint::test_discovery_endpoint_returns_200
```

### Esegui test con output verboso

```bash
uv run pytest -v

# Con output ancora più dettagliato
uv run pytest -vv
```

### Esegui test con coverage

```bash
# Installa coverage
uv pip install pytest-cov

# Esegui test con coverage
uv run pytest --cov=. --cov-report=html

# Apri il report HTML
open htmlcov/index.html
```

## 📁 Struttura Test

```
tests/
├── __init__.py                 # Package marker
├── conftest.py                 # Fixture pytest condivise
├── test_endpoints.py           # Test per gli endpoint FastAPI
├── test_jwks_service.py        # Test per il servizio JWKS
├── test_claims_generator.py   # Test per il generatore di claims
├── test_models.py              # Test per i modelli Pydantic
└── test_config.py              # Test per la configurazione
```

## 🧪 Tipologie di Test

### Test degli Endpoint (`test_endpoints.py`)

Testa tutti gli endpoint OIDC:
- **Discovery Endpoint**: Verifica la configurazione OIDC
- **JWKS Endpoint**: Verifica le chiavi pubbliche
- **Authorization Endpoint**: Verifica il flusso di autorizzazione
- **Token Endpoint**: Verifica lo scambio di token
- **UserInfo Endpoint**: Verifica le informazioni utente
- **Health Endpoint**: Verifica lo stato del server

### Test del Servizio JWKS (`test_jwks_service.py`)

Testa la generazione e gestione delle chiavi RSA:
- Inizializzazione del servizio
- Generazione chiavi PEM
- Formato JWKS
- Consistenza delle chiavi

### Test del Generatore Claims (`test_claims_generator.py`)

Testa la generazione dinamica dei claims:
- Parsing dei nomi dalle email
- Generazione UUID deterministici
- Gestione di diversi formati email
- Consistenza dei tenant ID

### Test dei Modelli (`test_models.py`)

Testa i modelli Pydantic:
- Validazione dei dati
- Campi obbligatori
- Valori di default
- Serializzazione JSON

### Test della Configurazione (`test_config.py`)

Testa le impostazioni dell'applicazione:
- Valori di default
- Scopes supportati
- Grant types supportati
- Configurazione dinamica

## 📊 Coverage

Il target di coverage dovrebbe essere almeno **80%**.

Per verificare il coverage:

```bash
uv run pytest --cov=. --cov-report=term-missing
```

## 🔧 Fixture Disponibili

### `test_client`
Client FastAPI TestClient per testare gli endpoint.

```python
def test_example(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
```

### `sample_user_email`
Email di test per utente mock.

```python
def test_example(sample_user_email):
    assert "@" in sample_user_email
```

### `sample_user_claims`
Claims di test completi.

```python
def test_example(sample_user_claims):
    assert "sub" in sample_user_claims
```

### `auth_params`
Parametri standard per authorization request.

```python
def test_example(test_client, auth_params):
    response = test_client.get("/authorize", params=auth_params)
```

### `pkce_params`
Parametri PKCE per authorization request.

```python
def test_example(auth_params, pkce_params):
    params = {**auth_params, **pkce_params}
```

## 🐛 Debug dei Test

### Esegui test con pdb

```bash
# Interrompi al primo fallimento
uv run pytest --pdb

# Interrompi ad ogni test
uv run pytest --trace
```

### Mostra print statements

```bash
uv run pytest -s
```

### Mostra variabili locali nei fallimenti

```bash
uv run pytest -l
```

## ✅ Best Practices

1. **Ogni test dovrebbe essere indipendente**: Non fare affidamento sull'ordine di esecuzione
2. **Usa fixture per setup comune**: Evita duplicazione di codice
3. **Testa edge cases**: Non solo il percorso felice
4. **Nomi descrittivi**: Il nome del test dovrebbe descrivere cosa testa
5. **Un assert per test**: Quando possibile, testa una cosa alla volta
6. **Cleanup automatico**: Le fixture si occupano del cleanup

## 🚨 CI/CD

I test vengono eseguiti automaticamente su ogni push tramite GitHub Actions.

Vedi `.github/workflows/test.yml` per la configurazione.

## 📝 Aggiungere Nuovi Test

1. Crea un nuovo file `test_*.py` nella directory `tests/`
2. Importa i moduli necessari e le fixture
3. Crea classi di test con nome `Test*`
4. Scrivi metodi di test con nome `test_*`
5. Usa assert per verificare i risultati

Esempio:

```python
"""
Test per il nuovo modulo
"""
import pytest

class TestNewFeature:
    """Test per la nuova funzionalità"""
    
    def test_feature_works(self):
        """Verifica che la funzionalità funzioni"""
        result = new_feature()
        assert result is True
```

## 🔗 Risorse

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/)
