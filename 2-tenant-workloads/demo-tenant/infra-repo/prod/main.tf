locals = {
    resource_name_prefix = "demo-tenant-my-python-app"
    tags = {
        Team        = "demo-tenant"
        Service     = "my-python-app"
        ManagedBy   = "terraform"
        Owner       = "demo-tenant"
    }
}

## Tenant Idempotent Infrastructure Modules ## - Do not remove these - Danger zone start!
module "aws-vpc" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-networking?ref=main"
    team_name = "demo-tenant"
    app_name  = "my-python-app"
    vpc_cidr  = "10.0.0.0/16"
}

module "aws-iam" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-iam?ref=main"
    team_name = "demo-tenant"
    app_name  = "my-python-app"
}
## Tenant Idempotent Infrastructure Modules ## - Do not remove these - Danger zone end!



module "aws-s3" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-s3?ref=main"
    team_name = "demo-tenant"
    app_name  = "my-python-app"
}

module "aws-postgres" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-postgres?ref=main"
    team_name = "demo-tenant"
    app_name  = "my-python-app"
}

