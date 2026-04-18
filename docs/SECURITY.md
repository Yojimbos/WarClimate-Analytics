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
- Local development uses environment variables and local-only configuration files outside source control.
- GitHub Actions uses Azure OpenID Connect with repository secrets only for Azure tenant, client, and subscription identifiers.
- Azure Key Vault stores selected platform-side secrets and metadata, including the ACR login server.
- Terraform state is stored in Azure Blob Storage, not in Key Vault.
- Kubernetes follows a documented secret management pattern with a future-ready path for SOPS or External Secrets.

## RBAC

- Namespaces are separated for `app`, `monitoring`, and `logging`.
- Service accounts are scoped per workload.
- GitHub Actions uses minimal permissions per workflow.
- Flux applies manifests with cluster-scoped resources limited to the GitOps operators and ingress or monitoring requirements.

## Network Restrictions

- Ingress is the only public entry point.
- API pods are protected by Kubernetes `NetworkPolicy`.
- PostgreSQL is intended to stay private to the VNet.
- The admin reimport endpoint should remain internal-only or be protected with API key and ingress restrictions in real deployments.

## Runtime Baseline

- Containers run as non-root where possible.
- Read-only root filesystems are enabled in Kubernetes manifests where practical.
- Security headers are configured at the application and ingress layers.
- Query parameters are validated for range size and date ordering before expensive work is triggered.

## CI/CD Security

- Dependency audit with `pip-audit`, `npm audit`, and CodeQL-ready scaffolding.
- Secret scanning via `gitleaks`.
- Container scanning via `trivy`.
- Image publishing uses Azure OIDC instead of long-lived cloud credentials where possible.
