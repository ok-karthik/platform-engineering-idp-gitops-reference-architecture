# 📦 Generated Applications & GitOps Architecture

This directory serves as the target output zone for the platform's **Internal Developer Platform (IDP) Scaffolder Generator**. It showcases the end-to-end scaffolding, GitOps layout, and deployment flow of generated microservices.

> [!NOTE]
> **Why is this nested inside the parent repository?**
> To ensure a **zero-setup, friction-free evaluation experience** for recruiters and architects, this folder acts as a local monorepo simulator. In a live enterprise deployment, these directories are automatically provisioned as separate, isolated GitHub/GitLab repositories.

---

## 🗺️ Single-Repository GitOps Loop (Demo Mode)

Since all code is stored in this main repository, standard nested workflow triggers won't run natively. To simulate a true multi-repo GitOps pipeline, we implement the **Single-Repository GitOps Loop** powered by a root-level orchestrator workflow ([demo-apps-ci-cd.yaml](file:///Users/karthik.orugonda/github/gitops-idp-blueprint/.github/workflows/demo-apps-ci-cd.yaml)):

```mermaid
graph TD
    subgraph Local Development
        Dev[1. Developer edits code under apps-source] --> Commit[2. Commit & Push to Main Repo]
    end

    subgraph GitHub Actions Orchestrator
        Commit -- triggers --#gt; GHA[3. Forwarder Workflow: demo-apps-ci-cd.yaml]
        GHA -- runs Helm template on --#gt; Render[4. Render manifest templates]
        Render -- commits & pushes changes --#gt; GitOpsDir[5. Updates gitops-repo/rendered-manifests]
    end

    subgraph GitOps Engine
        GitOpsDir -- webhook/poll --#gt; ArgoCD[6. ArgoCD detects change]
        ArgoCD -- reconciles state --#gt; K8s[7. Deploys to Local Cluster]
    end

    style Local Development fill:#1f2937,stroke:#4b5563,stroke-width:2px,color:#fff
    style GitHub Actions Orchestrator fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff
    style GitOps Engine fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff
```

---

## 🏛️ Architectural Modes

This platform is architected to seamlessly transition from local exploration to full enterprise-grade scale:

### 1. Local Demo Mode (Active)
* **Target Output:** Stored locally in `/generated-apps/[tenant-name]/`.
* **CI/CD Mechanism:** A single root-level GitHub Action (`demo-apps-ci-cd.yaml`) scans for changes inside `generated-apps/`, executes the compilation scripts (`helm template`), and commits the results back to the repository.
* **ArgoCD Syncing:** ArgoCD watches the local directory tree of this repository, synchronizing changes immediately into the local Kubernetes cluster.

### 2. Enterprise Production Mode (Pluggable)
* **Target Output:** Provisioned dynamically as isolated GitHub/GitLab repositories under a defined Organization.
* **CI/CD Mechanism:** The generator activates a **Publisher Plugin**. When a developer scaffolds an app:
  1. The IDP makes API calls to create separate repositories: `<tenant>-<app-name>-source`, `<tenant>-gitops`, and `<tenant>-infra`.
  2. It initializes local Git, commits the scaffolded templates, and pushes to the respective remotes.
  3. The `ci.yaml` pipeline inside the application source repository builds/pushes the Docker image and updates the image tag in `<tenant>-gitops`.
* **ArgoCD Syncing:** ArgoCD watches the team-specific GitOps repository (`<tenant>-gitops`) directly.

---

## 📊 GitOps Repository Models: Trade-offs

During design phases, we evaluated two GitOps repository structures. This platform implements **Option 2 (Repository-per-Tenant)** to optimize for enterprise scalability.

| Architectural Dimension | Option 1: Repository-per-App (Micro-GitOps) | Option 2: Repository-per-Tenant (Shared-GitOps) <br>**[SELECTED]** |
| :--- | :--- | :--- |
| **Blast Radius** | **Excellent:** An error in App A's values file has zero impact on App B. | **Medium:** Syntax errors in shared configuration files could temporarily block syncs for other apps in the same tenant group. |
| **Platform/ArgoCD Overhead** | **High:** Requires managing distinct repository credentials and ArgoCD Application custom resources for every single app. Easy to hit GitHub API rate limits. | **Low:** ArgoCD maintains **only one connection per team/tenant**. New apps are auto-discovered dynamically via ArgoCD `ApplicationSets` scanning the repo. |
| **Promotion (Dev to Prod)** | **Scattered:** Requires managing promotions across multiple independent pipelines and repositories. | **Unified:** Environment promotion is managed easily using branches (`main` -> `prod`) or environment directories in a single repo. |
| **Developer Autonomy** | **Segmented:** Developers manage two distinct repos per microservice. | **Holistic:** The team has a single repository representing the complete "state of the world" for their namespace. |

---

## 🔌 Backstage Integration & Pluggability

The generation templates and scripting logic in this blueprint are designed to be **directly compatible with Backstage** (the industry-standard open-source developer portal). 

If you migrate this blueprint to Backstage, the components map as follows:

1. **Software Templates:** Your templates under `/scaffolder-generator/templates/` map directly to Backstage `template.yaml` definitions.
2. **Variable Substitution:** The Jinja2 rendering engine used in `cli.py` maps to Backstage's **Nunjucks** templating parser (which shares the exact same `{{ variable }}` syntax).
3. **Repository Publishing:** Backstage provides built-in actions (`publish:github`, `publish:gitlab`) which replace the local folder generation with automated REST calls to create and push to separate remote repositories.
4. **Registration:** Backstage executes a `catalog:register` action to automatically add the scaffolded microservice to the developer portal's Software Catalog.
