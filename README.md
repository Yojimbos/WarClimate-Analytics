# WarClimate_Analytics

Portfolio-grade demo that visualizes official daily enemy personnel loss data against historical weather baselines for Ukraine. The solution focuses on historical ingestion, transparent data provenance, and a cost-aware cloud-native deployment path on Azure.

## What This Repository Contains

- FastAPI backend with ingestion jobs, analytics endpoints, Prometheus metrics, and PostgreSQL persistence.
- Responsive web UI built with vanilla JavaScript, Chart.js, and clean light/dark-friendly styling.
- Terraform for Azure foundational infrastructure.
- Kubernetes manifests with FluxCD GitOps structure.
- Prometheus, Grafana, and Loki starter manifests and dashboard provisioning.
- GitHub Actions workflows for CI, image build, infra validation, deployment automation, and security checks.

## Demo Screenshots

- `docs/screenshots/` 

## Architecture Overview

- Official losses source: Ministry of Defence of Ukraine article pages on `mod.gov.ua`.
- Weather source: Open-Meteo archive API for historical daily reference weather.
- Backend computes rolling averages, Pearson and Spearman correlations, summary cards, and chart-ready series.
- Frontend queries the REST API and renders charts, tables, source cards, and limitations.
- Azure target footprint: AKS, ACR, Azure Database for PostgreSQL Flexible Server, Azure Key Vault, and public ingress only.

Project documentation lives under [`docs/`](docs):

- [Architecture](docs/ARCHITECTURE.md)
- [Security](docs/SECURITY.md)
- [Operations](docs/OPERATIONS.md)
- [GitHub setup](docs/GITHUB_SETUP.md)
- [Terraform bootstrap](docs/TERRAFORM_BOOTSTRAP.md)

## Quick Start: Local

### Prerequisites

- Docker Desktop or compatible Docker Engine
- Python 3.12 for direct local backend commands

### Start Everything

```bash
make run
```

Frontend will be available on `http://localhost:8080` and backend on `http://localhost:8000`.

### Seed Sample Data

```bash
make seed
```

### Run Tests

```bash
make test
```

## Quick Start: Cloud

1. Provision Azure baseline with Terraform under `infra/terraform`.
2. Bootstrap Terraform remote state in Azure Storage before switching the main stack to remote backend.
2. Bootstrap Flux against the AKS cluster.
3. Push backend and frontend images to ACR through GitHub Actions.
4. Update image tags through Flux-managed manifests.
5. Apply secrets through the documented secret management pattern.

See [docs/OPERATIONS.md](docs/OPERATIONS.md) for deployment and day-2 steps.

## Data Sources

### Official losses data

- Ministry of Defence of Ukraine news pages on `https://mod.gov.ua/en/news/`
- Example pattern: `https://mod.gov.ua/en/news/total-russian-combat-losses-in-ukraine-as-of-april-17-2026`
- Official pages publish cumulative combat loss totals, and this demo derives daily personnel deltas by comparing consecutive official publication dates.

### Weather data

- Open-Meteo historical archive API: `https://open-meteo.com/en/docs/historical-weather-api`

## Location Strategy

This demo uses a documented weather proxy strategy instead of claiming battlefield-specific weather accuracy. Users can choose from three reference locations near the active combat zone context for the demo: `Kharkiv`, `Dnipro`, and `Zaporizhzhia`. This keeps the UI simple while being more honest about the intended analytical framing.

## Limitations

- Correlation does not imply causation. The application does not infer operational conclusions.
- Official losses publications can occasionally change wording or publish timing, so ingestion uses defensive parsing and run tracking.
- Weather is a reference proxy for a chosen location, not a geospatial reconstruction of combat conditions.
- Local development uses the official losses adapter and Open-Meteo by default, while sample seed data remains available for offline smoke testing.

## Security Notes

- No secrets are stored in the repository.
- Azure Key Vault stores platform-side secret and metadata values, including the ACR login server.
- Terraform state should be stored in Azure Blob Storage, not in Key Vault.
- Admin reimport endpoint requires a dedicated API key and is intended for internal use only.
- Containers run as non-root with read-only filesystems in Kubernetes where possible.
- NetworkPolicy, security headers, RBAC, and GitHub Actions least-privilege defaults are included.

## Cost-Aware Design

- PostgreSQL runs as Azure Database for PostgreSQL Flexible Server instead of self-hosting in AKS.
- AKS is sized for a practical demo footprint with system and workload separation documented as an optional upgrade, not a hard requirement.
- Observability uses lightweight in-cluster OSS tooling suitable for a demo.
- Log Analytics is intentionally omitted from the default Terraform footprint to keep spend lower and avoid duplicate logging pipelines.

## TODO

- Add browser-based smoke tests for the dashboard filter flow.
- Add screenshot assets and optional E2E browser smoke tests.
- Add SOPS or External Secrets Operator if the demo needs stronger GitOps secret automation.
