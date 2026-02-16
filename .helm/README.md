# Mock OIDC Helm Chart

Helm chart per il deployment del Mock OIDC Server su cluster Kubernetes.

## 📋 Prerequisiti

- Kubernetes 1.19+
- Helm 3.0+
- kubectl configurato per accedere al cluster

## 🚀 Installazione

### Installazione Base

```bash
# Dal root del progetto
helm install mockoidc .helm/

# Con custom values
helm install mockoidc .helm/ -f my-values.yaml

# In un namespace specifico
helm install mockoidc .helm/ -n oidc-system --create-namespace
```

### Installazione su Kind (Local Development)

Per esporre il servizio all'esterno del cluster kind, il cluster deve essere creato con port mapping:

```bash
# 1. Crea cluster kind con port mapping
cat <<EOF | kind create cluster --name mockoidc-dev --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30080  # NodePort del service
    hostPort: 8080        # Porta su localhost
    protocol: TCP
EOF

# 2. Build e load immagine
docker build -t mockoidc:latest ..
kind load docker-image mockoidc:latest --name mockoidc-dev

# 3. Deploy con values-dev (NodePort configurato)
helm install mockoidc .helm/ -f .helm/values-dev.yaml

# 4. Accesso dal browser
curl http://localhost:8080/health
# Oppure apri: http://localhost:8080/docs
```

> 📖 **Guida completa Kind**: [KIND.md](KIND.md)

### Installazione con Dry-Run

```bash
# Verifica cosa verrà creato
helm install mockoidc .helm/ --dry-run --debug
```

## ⚙️ Configurazione

### Parametri Principali

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `replicaCount` | Numero di repliche | `1` |
| `image.repository` | Repository dell'immagine | `mockoidc` |
| `image.tag` | Tag dell'immagine | `latest` |
| `image.pullPolicy` | Policy di pull dell'immagine | `IfNotPresent` |
| `service.type` | Tipo di servizio K8s | `ClusterIP` |
| `service.port` | Porta del servizio | `8080` |
| `ingress.enabled` | Abilita Ingress | `false` |
| `resources.limits.cpu` | Limite CPU | `500m` |
| `resources.limits.memory` | Limite memoria | `512Mi` |
| `resources.requests.cpu` | Richiesta CPU | `100m` |
| `resources.requests.memory` | Richiesta memoria | `128Mi` |

### Configurazione OIDC

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `config.port` | Porta del server | `8080` |
| `config.dynamicClaims.enabled` | Abilita dynamic claims | `true` |
| `config.dynamicClaims.defaultRoles` | Ruoli di default | `["User"]` |
| `config.dynamicClaims.defaultGroups` | Gruppi di default | `["Everyone"]` |
| `config.mockUsers` | Lista utenti pre-configurati | `[]` |

> **🔄 URL Dinamici**: `issuer` e `base_url` sono calcolati **automaticamente** dal server in base all'host della richiesta HTTP. Non è necessario configurarli. Il server si adatta a localhost, IP, DNS, Ingress hostname, ecc.

### Autoscaling

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Abilita HPA | `false` |
| `autoscaling.minReplicas` | Repliche minime | `1` |
| `autoscaling.maxReplicas` | Repliche massime | `10` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU % | `80` |

## 📝 Esempi di Configurazione

### 1. Deployment Base con Dynamic Claims

**Per Kind/Minikube (con accesso esterno tramite NodePort)**:
```yaml
# values-dev.yaml
service:
  type: NodePort
  port: 8080
  nodePort: 30080  # Accessibile su localhost:8080 con kind port mapping

config:
  port: 8080
  # issuer viene calcolato automaticamente (http://localhost:8080)
  dynamicClaims:
    enabled: true
    defaultRoles:
      - "User"
      - "Developer"
    defaultGroups:
      - "Everyone"
      - "Engineering"
    defaultTenantId: "company-tenant-123"
```

```bash
# Deploy su kind
helm install mockoidc .helm/ -f .helm/values-dev.yaml

# Accesso: http://localhost:8080
# (richiede cluster kind creato con extraPortMappings, vedi .helm/KIND.md)
```

**Per cluster cloud (con Ingress)**:
```yaml
# values-dynamic.yaml
config:
  port: 8080
  # issuer viene calcolato automaticamente (https://mockoidc.example.com)
  dynamicClaims:
    enabled: true
    defaultRoles:
      - "User"
      - "Developer"
    defaultGroups:
      - "Everyone"
      - "Engineering"
    defaultTenantId: "company-tenant-123"

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: mockoidc.example.com
      paths:
        - path: /
          pathType: Prefix
```

```bash
helm install mockoidc .helm/ -f values-dynamic.yaml
```

> **✨ Nota**: Con Ingress, l'issuer sarà automaticamente `https://mockoidc.example.com` basato sull'hostname della richiesta.

### 2. Deployment con Utenti Pre-configurati

```yaml
# values-preconfigured.yaml
config:
  # Note: issuer and base_url are calculated automatically from HTTP request host
  dynamicClaims:
    enabled: false
  mockUsers:
    - email: "admin@company.com"
      password: "admin123"
      claims:
        name: "Admin User"
        given_name: "Admin"
        family_name: "User"
        roles: ["Admin", "User"]
        groups: ["Administrators"]
    - email: "test@company.com"
      password: "test123"
      claims:
        name: "Test User"
        given_name: "Test"
        family_name: "User"
        roles: ["User"]
        groups: ["Testers"]

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 200m
    memory: 256Mi
```

```bash
helm install mockoidc .helm/ -f values-preconfigured.yaml
```

### 3. High Availability Setup

```yaml
# values-ha.yaml
replicaCount: 3

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 256Mi

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - mockoidc
        topologyKey: kubernetes.io/hostname
```

```bash
helm install mockoidc .helm/ -f values-ha.yaml
```

### 4. Con Ingress e TLS

```yaml
# values-ingress-tls.yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: mockoidc.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: mockoidc-tls
      hosts:
        - mockoidc.example.com

# Note: config.issuer not needed - calculated automatically from request host
```

```bash
helm install mockoidc .helm/ -f values-ingress-tls.yaml
```

## 🔧 Gestione

### Upgrade

```bash
# Upgrade con nuovi values
helm upgrade mockoidc .helm/ -f my-values.yaml

# Upgrade forzato
helm upgrade mockoidc .helm/ --force
```

### Rollback

```bash
# Lista delle release
helm history mockoidc

# Rollback all'ultima versione
helm rollback mockoidc

# Rollback a versione specifica
helm rollback mockoidc 3
```

### Disinstallazione

```bash
# Disinstalla release
helm uninstall mockoidc

# Disinstalla da namespace specifico
helm uninstall mockoidc -n oidc-system
```

## 🔍 Verifica

### Check dello Stato

```bash
# Status della release
helm status mockoidc

# Lista delle risorse
kubectl get all -l app.kubernetes.io/instance=mockoidc

# Logs
kubectl logs -l app.kubernetes.io/name=mockoidc -f
```

### Test degli Endpoint

```bash
# Port-forward per test locale
kubectl port-forward svc/mockoidc 8080:8080

# Test discovery endpoint
curl http://localhost:8080/.well-known/openid-configuration

# Test health endpoint
curl http://localhost:8080/health
```

## 🐛 Troubleshooting

### Pod non si avvia

```bash
# Descrivi il pod
kubectl describe pod -l app.kubernetes.io/name=mockoidc

# Visualizza eventi
kubectl get events --sort-by='.lastTimestamp'
```

### Problemi di Rete

```bash
# Test connettività dal pod
kubectl exec -it <pod-name> -- curl http://localhost:8080/health

# Verifica service endpoints
kubectl get endpoints mockoidc
```

### Image Pull Errors

Se l'immagine non è in un registry pubblico:

```yaml
imagePullSecrets:
  - name: my-registry-secret

image:
  repository: myregistry.example.com/mockoidc
  tag: "1.0.0"
```

## 📊 Monitoring

### Prometheus

```yaml
# values-monitoring.yaml
podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
  prometheus.io/path: "/metrics"
```

### Grafana Dashboard

Dopo aver installato Prometheus, puoi importare dashboard per monitorare:
- Request rate
- Latency
- Token generation
- Error rate

## 🔐 Security Best Practices

1. **Non usare l'immagine `latest` in produzione**:
```yaml
image:
  tag: "1.0.0"
```

2. **Configura resource limits**:
```yaml
resources:
  limits:
    cpu: 500m
    memory: 512Mi
```

3. **Usa NetworkPolicies** per limitare il traffico

4. **Abilita Pod Security Standards**

5. **Usa secret per credenziali sensibili**:
```bash
kubectl create secret generic mockoidc-secrets \
  --from-literal=admin-password=<password>
```

## 📚 Riferimenti

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Mock OIDC Server Documentation](../README.md)
- [OpenID Connect Specification](https://openid.net/connect/)

## 🤝 Supporto

Per problemi o domande, aprire una issue nel repository GitHub.
