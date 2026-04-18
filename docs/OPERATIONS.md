# Operations

## Verify Ingestion

- Check backend logs for adapter activity, source URLs, and upsert counts.
- Query `GET /api/v1/summary` or `GET /api/v1/correlation` for the expected date range and location.
- Inspect `ingestion_runs` in PostgreSQL for status, start time, and error details.

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
python -m app.cli ingest --days 30 --location kharkiv
```

### API

Send `POST /api/v1/admin/reimport` with the admin API key header and a supported location:

- `kharkiv`
- `dnipro`
- `zaporizhzhia`

## Update Dashboards

- Modify JSON dashboards under `monitoring/grafana/dashboards`.
- Commit changes and let Flux reconcile the Grafana ConfigMap.
- Confirm dashboard provisioning in Grafana logs.

## Local Demo Notes

- `docker compose up -d postgres backend frontend` starts the local stack.
- `make seed` loads sample data for offline smoke testing.
- By default, the local backend uses the official Ministry of Defence losses adapter and the Open-Meteo weather adapter.
