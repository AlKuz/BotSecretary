variable "namespace" {
  description = "The project namespace to use for unique resource naming"
  default     = "bot-secretary"
  type        = string
}

variable "region" {
  description = "AWS region"
  default     = "eu-central-1"
  type        = string
}