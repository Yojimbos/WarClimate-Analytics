variable "subscription_id" {
  type        = string
  description = "Azure subscription id."
}

variable "location" {
  type        = string
  default     = "westeurope"
  description = "Azure region for the Terraform state resources."
}

variable "project_name" {
  type    = string
  default = "war-climate-analytics"
}

variable "environment" {
  type    = string
  default = "dev"
}

