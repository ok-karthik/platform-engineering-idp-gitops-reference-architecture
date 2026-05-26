# 🏛️ Platform Engineering: IDP & GitOps Reference Architecture

An enterprise-grade **Internal Developer Platform (IDP)** blueprint designed for zero-touch onboarding, strict policy governance, and seamless multi-tenant continuous delivery via GitOps.

This repository serves as a reference architecture for platform teams looking to build "Local-to-Cloud" environments where developers are shielded from infrastructure complexity while retaining full deployment autonomy.

---

## 🏗️ Architecture Summary

As cloud-native architectures scale, cognitive load on product engineering teams becomes a critical bottleneck. This reference architecture implements a **Platform-as-a-Product** model using a "Control Plane" approach. 

By abstracting infrastructure and deployment patterns into declarative APIs and standardized templates, we enable:
* **Zero-Touch Provisioning:** Microservices are scaffolded and instantly deployed without platform team intervention.
* **Soft Multi-Tenancy:** Automated isolation of namespaces, network policies, and progressive delivery pipelines per product team.
* **Guardrails over Gates:** Pre-flight compliance and security enforcement through admission controllers (Kyverno) rather than manual ticket reviews.

---

## 🗺️ Architectural Topologies

### 1. The GitOps Reconciliation Loop
This platform enforces a strict, unidirectional flow of state. Kubernetes is treated as the source of truth, and Argo CD acts as the reconciliation engine.

```mermaid
graph TD
    subgraph Developer Experience
        Dev[Product Engineer] --> |Uses Scaffolder CLI| Code[Generates App & Manifests]
        Code --> |Pushes to| GitSource[(Tenant Git Repository)]
    end

    subgraph CI/CD Orchestration
        GitSource --> |Triggers| GHA[GitHub Actions]
        GHA --> |Tests & Compiles| Rendered[Rendered Manifests]
        Rendered --> |Commits to| GitOpsRepo[(Tenant GitOps Repo)]
    end

    subgraph Platform Control Plane
        AppSet((Argo CD ApplicationSet)) -.-> |Scans for new apps| GitOpsRepo
        GitOpsRepo --> |Syncs State| ArgoCD[Argo CD Core]
        ArgoCD --> |Reconciles| K8s[Kubernetes Cluster]
    end

    style Developer Experience fill:#1f2937,stroke:#4b5563,stroke-width:2px,color:#fff
    style CI/CD Orchestration fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff
    style Platform Control Plane fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff
```

### 2. Zero-Touch Multi-Tenant Auto-Discovery
To scale across hundreds of microservices, we utilize **Argo CD ApplicationSets**. Instead of manually mapping each microservice to an Argo CD `Application` resource, our ApplicationSet uses a multi-level Git directory generator (`apps/*/*-gitops-repo/apps/*`) to dynamically provision and isolate tenant applications on the fly.

---

## 📂 Project Structure & Scaffolding Strategy

The platform includes a custom **IDP Scaffolder Generator** (`/scaffolder-generator/`) acting as a blueprint engine. It generates boilerplate microservices, CI/CD pipelines, and GitOps configurations based on organizational best-practice templates.

### Monorepo Simulator (Demo Mode)
For simplicity and zero-setup evaluation, the generated output is stored locally within the [generated-apps](./generated-apps/README.md) directory of this repository. This simulates a monorepo setup and allows ArgoCD to sync directly from local directories.

However, in a **production enterprise environment**, the platform is designed to decouple these assets into separate, isolated Git repositories (e.g., `<tenant>-<app-name>-source` and `<tenant>-gitops`).

> For a deeper dive into the CI/CD orchestrator loop and how this transitions to production repository models, see the [Generated Applications & GitOps Architecture](./generated-apps/README.md) guide.

---

## 🧰 Component Matrix

This blueprint integrates best-in-class cloud-native tooling to form a cohesive ecosystem:

| Capability | Technology | Architectural Purpose |
| :--- | :--- | :--- |
| **Local Cluster** | **K3d (K3s)** | Lightweight, ephemeral Kubernetes environment optimized for ARM64/Silicon. |
| **GitOps Engine** | **Argo CD** | Declarative CD, state reconciliation, and multi-tenant auto-discovery. |
| **Infra as Code** | **Crossplane** | Abstracts AWS/Azure infrastructure into higher-level Kubernetes `Claims`. |
| **Policy as Code** | **Kyverno** | Admission control. Enforces cluster security boundaries and standards. |
| **Prog. Delivery** | **Argo Rollouts** | Automated Canary & Blue-Green deployments integrated with edge routing. |
| **Edge Gateway** | **Traefik** | L7 ingress, API gateway, rate-limiting, and middleware injection. |
| **Secrets Ops** | **Sealed Secrets** | Asymmetric encryption enabling safe storage of secrets in Git. |
| **Observability** | **Grafana Stack**| Unified metrics (Prometheus), logs (Loki), and traces (Tempo). |

---

## 🚀 Deployment Guide (Local Demo Mode)

You can spin up this entire reference architecture locally to evaluate the developer experience and platform guardrails. We provide a `Makefile` to simplify the setup process.

### 1. Provision the Ephemeral Cluster
```bash
make create-cluster
```

### 2. Install the GitOps Engine (Argo CD)
```bash
make install-argocd
```

### 3. Bootstrap the Platform
The `bootstrap.yaml` file acts as the root of the "App of Apps" pattern. It points Argo CD to the `platform-charts/` directory to deploy all cluster add-ons simultaneously.
```bash
make bootstrap
```

> **Tip:** You can also run `make setup` to perform all cluster provisioning, Argo CD installation, and bootstrapping in one command.

### 4. Scaffold a New Microservice
Emulate a developer onboarding a new service. The generator builds the source code, pipelines, and GitOps configurations.
```bash
./scaffolder-generator/.venv/bin/python ./scaffolder-generator/cli.py \
  -a my-payment-service \
  -t springboot \
  -p 8080 \
  -team finance-team
```

---

## 🔮 Future Roadmap

To mature this architecture for production environments, the following capabilities are roadmapped:

- [ ] **Backstage Integration:** Migrating the python CLI generator into Backstage Software Templates for a unified GUI developer portal.
- [ ] **AIOps / Observability:** Full instrumentation using OpenTelemetry to map service dependencies and reduce MTTR via correlation.
- [ ] **FinOps Automation:** Operator-driven cost controls to scale non-production idle workloads to zero using KEDA.
- [ ] **Cross-Cloud Capabilities:** Expanding Crossplane Compositions to support Azure AKS and GCP GKE multi-cloud environments.
