# GitHub Setup

## Repository Secrets

Configure the following repository secrets before enabling container publishing and deployment workflows:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `ACR_LOGIN_SERVER`

## Optional Runtime Secrets

These should not be stored in GitHub unless your deployment process requires them there:

- `DATABASE_URL`
- `ADMIN_API_KEY`
- `GRAFANA_ADMIN_PASSWORD`

## Recommended GitHub Settings

- Protect the `main` branch.
- Require pull request review before merge.
- Require `backend-ci`, `frontend-ci`, `infra-validate`, and `security` checks.
- Restrict GitHub Actions to approved actions if your org policy allows it.

## Azure Identity Pattern

Use GitHub OpenID Connect with a federated credential on an Azure Entra application:

1. Create an Azure application registration for GitHub Actions.
2. Add a federated credential scoped to the repository and `main` branch.
3. Grant the principal access to push images to ACR and, if needed, read deployment metadata.
4. Store the resulting application identifiers as repository secrets.

## Flux Image Update Flow

The current workflow updates `k8s/overlays/dev/kustomization.yaml` with the current `GITHUB_SHA`.
For a more scalable setup, replace this with Flux image automation controllers in a future iteration.
