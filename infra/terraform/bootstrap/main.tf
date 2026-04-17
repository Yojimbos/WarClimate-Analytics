locals {
  state_prefix = "${var.project_name}-${var.environment}-tfstate"
  normalized   = replace(local.state_prefix, "-", "")
  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform-bootstrap"
  }
}

resource "random_string" "suffix" {
  length  = 5
  upper   = false
  special = false
}

resource "azurerm_resource_group" "this" {
  name     = "${var.project_name}-tfstate-rg"
  location = var.location
  tags     = local.tags
}

resource "azurerm_storage_account" "this" {
  name                            = substr("${local.normalized}${random_string.suffix.result}", 0, 24)
  resource_group_name             = azurerm_resource_group.this.name
  location                        = azurerm_resource_group.this.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = true
  tags                            = local.tags

  blob_properties {}
}

resource "azurerm_storage_container" "this" {
  name                  = "tfstate"
  storage_account_id    = azurerm_storage_account.this.id
  container_access_type = "private"
}

