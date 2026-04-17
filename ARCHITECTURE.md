# Architecture

## High-Level Architecture

The system is composed of four primary layers:

1. Data ingestion jobs fetch official losses data from the Ministry of Defence of Ukraine and historical weather data from Open-Meteo.
2. The FastAPI backend normalizes, stores, and serves curated daily records and analytics from PostgreSQL.
3. The frontend dashboard consumes backend APIs and renders charts, tables, filters, and disclaimers.
4. Azure hosts the runtime stack with AKS, ACR, PostgreSQL Flexible Server, and FluxCD GitOps delivery.

## Data Flow

1. A CronJob or manual admin call triggers ingestion.
2. Losses adapter constructs official article URLs for each requested date, parses cumulative personnel totals from official pages, and derives daily deltas by comparing consecutive dates.
3. Weather adapter fetches daily archive values for a selected reference location.
4. Ingestion services upsert records into `losses_daily` and `weather_daily`.
5. Analytics service joins records by date and location, calculates rolling averages and correlation metrics, then serves chart-ready payloads.

## Deployment Flow

1. Terraform provisions Azure primitives.
2. GitHub Actions builds and pushes application images to ACR.
3. Flux watches the repository and reconciles Kubernetes manifests in the dev overlay.
4. Ingress exposes the UI and API through TLS.

## Observability Flow

- Backend exposes Prometheus metrics on `/metrics`.
- Prometheus scrapes the backend via `ServiceMonitor`.
- Grafana reads Prometheus and Loki datasources and loads provisioned dashboards from the repository.
- Loki stores application, ingress, and ingestion job logs via Promtail.

## Networking Notes

- Only the ingress controller receives public traffic.
- PostgreSQL Flexible Server is configured for private access in the recommended path.
- NetworkPolicy restricts east-west communication to required namespaces and ports.
