# Operations

## Verify Ingestion

- Check backend logs for `ingestion_run_id`, source adapter details, and upsert counts.
- Query `GET /api/v1/summary` for the expected date range.
- Inspect `ingestion_runs` in PostgreSQL for status, started time, and error details.

## View Logs

- Application logs are emitted as structured JSON.
- Use Loki labels for `namespace`, `app`, and `job`.
- In local development, use `docker compose logs backend`.

## Verify Metrics

- Open `GET /metrics` on the backend.
- In-cluster, confirm Prometheus target health and Grafana dashboards.
- Focus on request latency, request rate, error rate, and ingestion duration metrics.

## Re-Run Import

### Local

```bash
cd backend
python -m app.cli ingest --days 30 --location kyiv
```

### API

Send `POST /api/v1/admin/reimport` with the admin API key header.

## Update Dashboards

- Modify JSON dashboards under `monitoring/grafana/dashboards`.
- Commit changes and let Flux reconcile the Grafana ConfigMap.
- Confirm dashboard provisioning in Grafana logs.

