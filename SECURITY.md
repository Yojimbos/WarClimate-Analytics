# Security

## Threat Model Lite

Primary risks for this demo are:

- Exposure of admin-only ingestion controls.
- Secret leakage through CI/CD or manifests.
- Excessive network reachability inside the cluster.
- Vulnerabilities in dependencies or container images.
- Unsanitized query inputs causing expensive or invalid data requests.

## Secrets Handling

- Secrets are not committed to Git.
- Local development uses environment variables and `.env` patterns outside source control.
- GitHub Actions pulls registry and deployment secrets from GitHub Secrets.
- Kubernetes uses a documented secret management pattern with a future-ready path for SOPS or External Secrets.

## RBAC

- Namespaces are separated for `app`, `monitoring`, and `logging`.
- Service accounts are scoped per workload.
- GitHub Actions uses minimal permissions per workflow.
- Flux applies manifests with cluster-scoped resources limited to the GitOps operators and ingress/monitoring requirements.

## Network Restrictions

- Ingress is the only public entry point.
- API pods are protected by Kubernetes `NetworkPolicy`.
- PostgreSQL is intended to stay private to the VNet.
- Admin reimport endpoint should be protected with an internal-only route, IP restriction, or API gateway rule in real deployments.

## CI/CD Security

- Dependency audit with `pip-audit`, `npm audit`, and CodeQL-ready scaffolding.
- Secret scanning via `gitleaks`.
- Container scanning via `trivy`.
- Image publishing uses OpenID Connect or scoped credentials where possible.

