output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "storage_account_name" {
  value = azurerm_storage_account.this.name
}

output "container_name" {
  value = azurerm_storage_container.this.name
}

output "backend_config" {
  value = {
    resource_group_name  = azurerm_resource_group.this.name
    storage_account_name = azurerm_storage_account.this.name
    container_name       = azurerm_storage_container.this.name
    key                  = "${var.environment}/terraform.tfstate"
    use_azuread_auth     = true
  }
}

