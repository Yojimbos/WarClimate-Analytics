# Architecture

## High-Level Architecture

The system is composed of four primary layers:

1. Data ingestion jobs fetch official losses data from the Ministry of Defence of Ukraine and historical weather data from Open-Meteo.
2. The FastAPI backend normalizes, stores, and serves curated daily records and analytics from PostgreSQL.
3. The frontend dashboard consumes backend APIs and renders charts, tables, filters, and disclaimers.
4. Azure hosts the runtime stack with AKS, ACR, PostgreSQL Flexible Server, Key Vault, and FluxCD GitOps delivery.

## Data Flow

1. A CronJob, CLI command, or admin reimport call triggers ingestion.
2. The official losses adapter reads the Ministry of Defence sitemap on `mod.gov.ua`, discovers relevant official article URLs for the requested dates, and parses published daily personnel loss values from official English-language pages.
3. The weather adapter fetches daily archive values from Open-Meteo for the selected reference location.
4. Ingestion services upsert normalized records into `losses_daily` and `weather_daily`.
5. API routes can trigger on-demand backfill when the requested date range or location has not been ingested yet.
6. The analytics service joins records by date and location, calculates rolling averages and correlation metrics, and returns chart-ready payloads.

## Location Strategy

The application intentionally avoids claiming battlefield-precise weather coverage. Instead, it uses three explicit reference cities:

- `Kharkiv`
- `Dnipro`
- `Zaporizhzhia`

These locations were selected because they provide a more credible demo baseline for eastern and southeastern Ukraine than a national capital baseline. They remain a proxy only and should not be interpreted as direct weather conditions for every reported combat event.

## Deployment Flow

1. Terraform bootstrap provisions remote state storage in Azure Blob Storage.
2. The main Terraform stack provisions Azure primitives and stores selected platform metadata in Key Vault.
3. GitHub Actions builds and pushes application images to ACR.
4. Flux watches the repository and reconciles Kubernetes manifests in the dev overlay.
5. Ingress exposes the UI and API through TLS.

## Observability Flow

- Backend exposes Prometheus metrics on `/metrics`.
- Prometheus scrapes the backend via `ServiceMonitor`.
- Grafana reads Prometheus and Loki datasources and loads provisioned dashboards from the repository.
- Loki stores application, ingress, and ingestion job logs via Promtail.

## Networking Notes

- Only the ingress controller receives public traffic.
- PostgreSQL Flexible Server is designed to remain private to the virtual network.
- NetworkPolicy restricts east-west communication to required namespaces and ports.
