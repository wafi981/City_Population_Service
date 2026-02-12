# Reflection 

## Challenges Faced During Implementation & Deployment


### 1️⃣ Docker Architecture Mismatch (ARM vs AMD64)

Issue:
The application was initially built on an Apple Silicon (ARM64) machine, while the Kubernetes cluster expected AMD64 images. This resulted in runtime errors such as:
```
exec format error
```

Root Cause:
Docker builds by default for the host architecture. A single-architecture image was incompatible with the cluster runtime.

Resolution:
Switched to Docker Buildx and built a multi-platform image:
```
docker buildx build --platform linux/amd64,linux/arm64 --push
```

This ensured compatibility across heterogeneous environments.

Learning:
Always consider target cluster architecture when building container images.


### 2️⃣ Kubernetes Health Probe Design

Issue:
Initially, all probes (startup, readiness, liveness) pointed to a single /health endpoint that always returned 200 OK, even if Elasticsearch was unavailable.

Risk:
Traffic could be routed to pods before Elasticsearch was ready, leading to failed API requests.

Resolution:
Separated health endpoints into:
```
/health → Assignment-required endpoint

/health/live → Liveness probe

/health/ready → Readiness & startup probe (checks Elasticsearch connectivity)
```

Learning:
Proper probe separation is critical for reliable cloud-native behavior.


### 3️⃣ OOMKilled (Elasticsearch)

During deployment, Elasticsearch pods experienced an OOMKilled error due to default JVM heap allocation exceeding the available container memory limits.
By default, Elasticsearch auto-allocates heap based on available memory, which caused the container to exceed its limits and be terminated by Kubernetes.

#### Solution:
We resolved it by explicitly defining ES_JAVA_OPTS to control heap allocation within Kubernetes resource boundaries.



## Suggestions To Run This Application In Production


### 1.) High Availability (HA) Architecture

For our application Deploy minimum 3 replicas and Distribute across multiple worker nodes

#### Enforce pod spreading using:
```
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
```
This ensures replicas do not run on the same node.

#### To guarantee availability during voluntary disruptions (node maintenance, upgrades).
Add a:
```
PodDisruptionBudget
minAvailable: 2
```

Please ensure you have 3 nodes in this setup.
If you only have:

2 nodes → One pod will stay Pending

1 node → Only 1 pod runs, others Pending



#### Horizontal Pod Autoscaling (HPA)

Enable autoscaling based on:

- CPU utilization (e.g., 70%)

- Memory thresholds

- Custom Prometheus metrics (RPS, latency)

Example:
```
minReplicas: 3
maxReplicas: 10
```

This ensures elastic scaling during traffic spikes while maintaining baseline availability.


### 2.) Database Setup: Elasticsearch Clustering Design

The current deployment can be upgraded to a resilient cluster architecture.

#### Recommended Setup

- Deploy Elasticsearch as a StatefulSet

- Minimum 3 replicas

- Dedicated PersistentVolumes

- Separate master and data nodes in larger environments


Why StatefulSet?

- Stable network identity

- Persistent storage binding

- Ordered startup and shutdown

- Required for clustered databases


With 3 replicas:
The cluster tolerates 1 node failure, it maintains quorum and Preserves write availability


### 3.) Backup & Restore Strategy

#### Implement automated snapshot policies:

- Snapshot repository (S3 / Azure Blob / MinIO)

- Scheduled backups (e.g., every 6 hours)

- Retention policy (7–30 days)

- Quarterly restore testing is required.

**Backups without restore validation are incomplete.**


### 4.) Multi-Region Disaster Recovery (DR)

For mission-critical systems:

#### Option A – Active/Passive

Primary region handles traffic

Secondary region replicates snapshots

#### Option B – Active/Active

Cross-region Elasticsearch replication

Global load balancing



### 5.) Security Hardening

Security must be layered and enforced across containers, infrastructure, and pipelines.

#### Container Hardening

```
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
```

Additional controls:

- Drop Linux capabilities

- Use minimal/distroless base images

- Enable image scanning (Trivy / Snyk)

#### Secrets Management

Avoid storing secrets in:

- Helm values

- Plain Kubernetes Secrets

Instead use:

- HashiCorp Vault or other External Secrets Operator

Helm charts should reference external secret providers.

#### Registry & Helm Repository Security

Docker images:

- Private registry (ACR / Harbor)

- Vulnerability scanning enabled

Helm charts:

- Private Helm repository (ChartMuseum / OCI registry)

- Versioned and signed

#### Network Security

- Implement Kubernetes NetworkPolicies

- Allow only required traffic (app → Elasticsearch)

- Enforce TLS for Elasticsearch communication

- Prevent public database exposure

### RBAC

- Minimal privilege model

- Dedicated service accounts

- No cluster-admin permissions for applications


### 6.) Observability Stack

A production-grade system requires full observability.

#### Metrics

- Prometheus, Node Exporter

- Grafana dashboards

- HPA metric integration

#### Logging

- Centralized logging (ELK / OpenSearch / Loki)

- Structured JSON logs

#### Tracing

- Jaeger or OpenTelemetry

### Alerting

- Alertmanager

- PagerDuty / Email / Slack integration

### Define SLOs such as:

- 99.9% availability

- <200ms API latency etc 


### 7.) Service Exposure Strategy

Currently, the application uses:
```
type: ClusterIP
```

This exposes the service only inside the Kubernetes cluster, which is correct for:

- Internal communication

- Backend services (e.g., Elasticsearch)

However, for production-grade external access:

#### Recommended Approach

- Use an Ingress Controller:
- Keep service as ClusterIP
- Expose externally via Ingress
- Enable TLS termination
- Domain-based routing
- Centralized traffic control

Why Ingress?
- HTTPS support
- More secure than NodePort
- More scalable than multiple LoadBalancers

Elasticsearch should always remain ClusterIP only and never be publicly exposed.



### 8.) CI/CD Maturity Improvements

Enhance pipeline reliability and security:

- Pre-commit linting

- SAST & dependency scanning

- Container scanning

- SBOM generation

- Multi-architecture builds (Buildx)

- Helm chart validation

- Progressive delivery (Blue-Green / Argo Rollouts)

Production pipelines should include:

- Manual approval gates

- GitOps deployment model (ArgoCD / Flux)