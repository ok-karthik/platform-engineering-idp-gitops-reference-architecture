# Golden Path Scaffolder (Control Plane)

This folder contains the **Golden Path Scaffolder API & CLI**, which serves as the control plane for tenant onboarding and application code scaffolding in our Internal Developer Platform (IDP).

It uses **FastAPI** to expose HTTP endpoints for developers, **Typer** to build a modern developer CLI, and **Copier** for template orchestration andDay-2 upgrades.

---

## Features

1. **Unified API & CLI Validation:** Shared Pydantic schemas validate project names, ports, and configurations.
2. **Deterministic IPAM:** Automatically assigns non-overlapping CIDR blocks to new tenant VPCs and registers them in `cloud_vpcs_allocated.yaml`.
3. **Copier Integration:** Renders standard GitOps and infrastructure modules cleanly using standard HCL variables.
4. **Editable CLI Packaging:** Can be installed locally in your shell as the `scaffolder` command.

---

## Getting Started

### 1. Installation

You can install the CLI directly into your active virtual environment in editable mode:

```bash
# From the root of the project
make install-scaffolder
```

This will register the `scaffolder` binary in your local environment path.

### 2. Using the CLI

Run the help command to see the available options:

```bash
scaffolder create --help
```

To scaffold a new application for a team, execute:

```bash
scaffolder create \
  --app-name my-python-app \
  --app-type python \
  --app-port 8080 \
  --team-name demo-tenant \
  --cloud-services aws-s3,aws-postgres
```

*Note: You can pass cloud services as a comma-separated list (`aws-s3,aws-postgres`) or as multiple flags (`-cs aws-s3 -cs aws-postgres`).*

### 3. Running the API

Start the FastAPI developer server:

```bash
# From the root of the project
make run-api
```

Open your browser to **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** to interact with the API endpoints.

---

## Architectural Layout

* `schemas.py`: Houses all Pydantic models (data-validation layer) and Enums.
* `utils.py`: Contains helper functions for reading filesystems and executing IPAM address allocation.
* `cli.py`: Declares the Typer command-line interface.
* `api.py`: Exposes HTTP API endpoints for integration with web portals.
* `main.py`: The main package entrypoint that delegates execution to the CLI.
* `templates/`: Base skeleton layouts for user workloads, infrastructure, and Helm charts.