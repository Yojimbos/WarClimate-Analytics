variable "subscription_id" {
  type        = string
  description = "Azure subscription id."
}

variable "location" {
  type        = string
  default     = "westeurope"
  description = "Azure region."
}

variable "project_name" {
  type    = string
  default = "enemy-losses-weather-demo"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "aks_node_count" {
  type    = number
  default = 2
}

variable "aks_vm_size" {
  type    = string
  default = "Standard_B4ms"
}

variable "postgres_admin_username" {
  type    = string
  default = "pgadmin"
}

variable "postgres_admin_password" {
  type        = string
  sensitive   = true
  description = "PostgreSQL admin password."
}

