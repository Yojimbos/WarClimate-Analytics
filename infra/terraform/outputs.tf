output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.this.name
}

output "acr_login_server" {
  value = azurerm_container_registry.this.login_server
}

output "ingress_public_ip" {
  value = azurerm_public_ip.ingress.ip_address
}

output "postgres_fqdn" {
  value = azurerm_postgresql_flexible_server.this.fqdn
}

