variable "team_name" {
  type        = string
  description = "Team/Tenant name"
}

variable "app_name" {
  type        = string
  description = "Application name"
}

provider "random" {}

resource "random_string" "bucket_suffix" {
  length  = 4
  lower   = true
  special = false
}

resource "aws_s3_bucket" "example" {
  bucket = "${var.team_name}-${var.app_name}-bucket-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "${var.team_name}-${var.app_name}-bucket"
    Team        = var.team_name
    Service     = var.app_name
    ManagedBy   = "terraform"
    Owner       = var.team_name
  }
}