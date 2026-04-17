# Terraform Bootstrap

## Why Bootstrap Exists

Terraform state should be stored in Azure Blob Storage, not in Key Vault. Key Vault is used for secrets and selected platform metadata, while the state backend should live in a dedicated storage account and private blob container.

## Bootstrap Flow

1. Run the bootstrap configuration in `infra/terraform/bootstrap`.
2. Capture the generated storage account details from Terraform outputs.
3. Copy `infra/terraform/backend.hcl.example` to a local `backend.hcl` file and fill in the real values.
4. Re-run `terraform init` in `infra/terraform` with `-backend-config=backend.hcl`.

## Bootstrap Commands

```bash
cd infra/terraform/bootstrap
terraform init
terraform apply -var="subscription_id=<subscription-id>"
terraform output -json backend_config
```

## Main Stack Init

```bash
cd infra/terraform
terraform init -backend-config=backend.hcl
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Key Vault Protection

- The main stack enables soft delete and purge protection on Key Vault.
- A `CanNotDelete` management lock is also applied to reduce accidental deletion risk.

## Recommended Local Files

Do not commit these files:

- `infra/terraform/backend.hcl`
- `infra/terraform/terraform.tfvars`
