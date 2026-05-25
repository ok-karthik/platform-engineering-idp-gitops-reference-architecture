# GitOps Internal Developer Platform (IDP) Blueprint

> ⚠️ **Under Development / Work In Progress**
> As of now, this is a non-functional repository demonstrating an architecture using tools like ArgoCD (App of Apps), Sealed Secrets, Cert Manager, and more. This project is actively being developed as a blueprint and will be expanded in the coming weeks/months.

A declarative Internal Developer Platform (IDP) designed for local-to-cloud infrastructure orchestration. This blueprint implements a "Local-First" Control Plane architecture to manage cloud resources and application lifecycles via GitOps.

The platform generator implements soft multi-tenancy, treating each developer team as a logical tenant with isolated namespaces, network policies, and dedicated observability stacks."

---

## 🏗️ Architecture

This repository uses the **App of Apps** pattern to manage platform services through a single root application.

### Components
| Layer | Service | Description |
| :--- | :--- | :--- |
| **Cluster** | K3d (k3s) | Local Kubernetes engine optimized for ARM64/Apple Silicon. |
| **GitOps** | Argo CD | Declarative continuous delivery engine. |
| **Control Plane** | Crossplane | Cloud infrastructure orchestration (AWS S3) using Composite Resources. |
| **Policy** | Kyverno | Kubernetes-native policy engine for admission control and validation. |
| **Delivery** | Argo Rollouts | Progressive delivery controller for Canary and Blue-Green deployments. |
| **Ingress** | Traefik | L7 ingress controller with custom middleware support. |
| **Security** | Sealed Secrets | Asymmetric encryption for secrets management. |

---

## Core Implementation Details

### 1. Unified Policy Governance (Kyverno)
The platform enforces architecture guardrails through `ClusterPolicy` resources:
- **Namespace Validation**: Ensures resources are deployed into designated project namespaces.
- **Resource Compliance**: Validates S3 bucket configurations (e.g., enforcing mandatory encryption).

### 2. Progressive Delivery (Argo Rollouts)
Standardizes deployment strategies across the platform. By integrating Argo Rollouts with Traefik, the blueprint supports weighted traffic shifting for Canary releases and automated rollback capabilities.

### 3. Edge Routing & Middlewares (Traefik)
The networking layer implements Traefik Middlewares for cross-cutting concerns:
- **Rate Limiting**: Protects platform endpoints from excessive traffic.
- **Security Headers**: Injects HSTS, XSS protection, and Frame-options at the gateway level.
- **Resilience**: Configurable retry logic for internal service communication.

### 4. Infrastructure-as-Code (Crossplane)
Cloud resources are abstracted through high-level `Claims`. The underlying `Composition` ensures that provisioned infrastructure adheres to organizational standards.

---

## Deployment Guide

### 1. Provision Cluster
```bash
k3d cluster create nexus-platform \
  --k3s-arg "--disable=traefik@server:0" \
  -p "80:80@loadbalancer" \
  -p "443:443@loadbalancer"
```

### 2. Install Argo CD
```bash
helm upgrade --install argocd argo/argo-cd \
  --namespace argocd \
  --reuse-values \
  --set server.extraArgs="{--insecure}" --create-namespace
```

### 3. Bootstrap Platform
```bash
kubectl apply -f bootstrap.yaml
```

### 4. Configure AWS Provider
```bash
kubectl create secret generic aws-creds -n crossplane-system --from-file=creds=./aws-creds.ini
```

---

## Developer Interface
Example of a developer claim for an AWS S3 bucket:
```yaml
apiVersion: platform.io/v1alpha1
kind: AWSBucket
metadata:
  name: prod-data-storage
  namespace: engineering
spec:
  parameters:
    bucketName: my-unique-bucket-id
    region: us-east-1
    isEncrypted: true
```

---

## 🗺️ Future Roadmap / Upcoming Features

- **OPA Gatekeeper / Kyverno Integration**: Advanced policy enforcement.
- **Backstage**: Developer portal integration to centralize service catalogs and templates.
- **Custom CLI**: A command-line interface to create new instances of Kubernetes clusters on the cloud pre-configured with these specific tools.
- **Platform Security Guardrails**: Mechanisms to restrict developers to certain safe changes in infrastructure components using policy-as-code tools.
- **Observability Stack**: Full metrics, logs, and traces using Loki, Grafana, and Tempo.
- **Continuous refinement**: Hardening the GitOps workflows and expanding the component catalog.

