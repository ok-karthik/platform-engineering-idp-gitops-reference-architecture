variable "team_name" {
  type        = string
  description = "Team/Tenant name"
}

variable "app_name" {
  type        = string
  description = "Application name"
}

provider "random" {}

resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "!@#$%&*"
  keepers = { engine_version = "16" }
}

resource "random_string" "db_suffix" {
  length  = 4
  lower   = true
  special = false
}

resource "aws_db_instance" "app_db" {
  identifier        = "${var.team_name}-${var.app_name}-db-${random_string.db_suffix.result}"
  engine            = "postgres"
  instance_class    = "db.t3.micro"
  username          = "admin"
  password          = random_password.db_password.result
  allocated_storage = 20

  tags = {
    Name        = "${var.team_name}-${var.app_name}-db"
    Team        = var.team_name
    Service     = var.app_name
    ManagedBy   = "terraform"
    Owner       = var.team_name
  }
}