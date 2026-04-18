# GitHub Setup

## Repository Secrets

Configure the following repository secrets before enabling container publishing and deployment workflows:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

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
- Add repository variable `ENABLE_CODE_SCANNING=true` only after GitHub Code Scanning is enabled for the repository.

## Azure Identity Pattern

Use GitHub OpenID Connect with a federated credential on an Azure Entra application:

1. Create an Azure application registration for GitHub Actions.
2. Add a federated credential scoped to the repository and `main` branch.
3. Grant the principal access to push images to ACR and, if needed, read deployment metadata.
4. Store the resulting application identifiers as repository secrets.

Recommended Azure roles for the GitHub OIDC principal:

- `Reader` on the resource group that contains the ACR and AKS resources.
- `AcrPush` on the Azure Container Registry.

## ACR And Key Vault

- `ACR_LOGIN_SERVER` is not required as a GitHub secret.
- Terraform creates Azure Container Registry and Azure Key Vault.
- Terraform stores the ACR login server in Key Vault as `acr-login-server`.
- The `container-build` workflow discovers the ACR directly from Azure after OIDC login, which avoids duplicating that value in GitHub.

## Flux Image Update Flow

- The container workflow publishes two tags for each image:
  - a commit-specific SHA tag
  - `latest`
- The Kubernetes manifests in this demo track `latest`.
- The deploy workflow runs only after a successful `container-build` workflow and restarts the workloads in AKS so the cluster pulls the newest `latest` image.
- This keeps docs-only or Terraform-only commits from advancing runtime image references to tags that were never built.

## Code Scanning

- The `security` workflow runs CodeQL only when the repository variable `ENABLE_CODE_SCANNING` is set to `true`.
- This avoids failing the workflow in repositories where GitHub Code Scanning has not been enabled yet.
- For public repositories, enable Code Scanning in GitHub repository settings first.
- For private repositories, Code Scanning may require GitHub Advanced Security depending on your plan.
