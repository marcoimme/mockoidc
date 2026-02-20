# Kubernetes Examples

Questa directory contiene esempi di configurazioni Kubernetes per casi d'uso specifici.

## 📁 Contenuto

- `namespace.yaml` - Namespace dedicato per Mock OIDC
- `network-policy.yaml` - NetworkPolicy per sicurezza del traffico
- `values-*.yaml` - Varie configurazioni Helm per scenari diversi

## 🚀 Utilizzo

### 1. Deploy con Namespace Dedicato

```bash
# Crea namespace
kubectl apply -f namespace.yaml

# Deploy con Helm nel namespace
helm install mockoidc ../.helm/ \
  -n mockoidc-system \
  -f ../values-dev.yaml

# Verifica
kubectl get all -n mockoidc-system
```

### 2. Deploy con Network Policy

```bash
# Applica network policy
kubectl apply -f network-policy.yaml

# Verifica
kubectl get networkpolicy -n mockoidc-system
```

## 📚 Esempi Specifici

### Ambiente di Sviluppo (Minikube/Kind)

```bash
# Load image in kind
kind load docker-image mockoidc:latest

# Deploy
helm install mockoidc ../.helm/ \
  -n mockoidc-system \
  --create-namespace \
  -f ../values-dev.yaml

# Port forward
kubectl port-forward -n mockoidc-system svc/mockoidc 8080:8080
```

### Ambiente di Staging

```bash
# Con ingress
helm install mockoidc ../.helm/ \
  -n mockoidc-staging \
  --create-namespace \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=mockoidc-staging.example.com
```

### Ambiente di Produzione

```bash
# Con HA e autoscaling
helm install mockoidc ../.helm/ \
  -n mockoidc-production \
  --create-namespace \
  -f ../values-prod.yaml \
  --set autoscaling.enabled=true
```
