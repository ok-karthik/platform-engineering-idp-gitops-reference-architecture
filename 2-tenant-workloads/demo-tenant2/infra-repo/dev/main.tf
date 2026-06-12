locals = {
    resource_name_prefix = "demo-tenant2-my-python-app2"
    tags = {
        Team        = "demo-tenant2"
        Service     = "my-python-app2"
        ManagedBy   = "terraform"
        Owner       = "demo-tenant2"
    }
}

## Tenant Idempotent Infrastructure Modules ## - Do not remove these - Danger zone start!
module "aws-vpc" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-networking?ref=main"
    team_name = "demo-tenant2"
    app_name  = "my-python-app2"
    vpc_cidr  = "10.1.0.0/16"
}

module "aws-iam" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-iam?ref=main"
    team_name = "demo-tenant2"
    app_name  = "my-python-app2"
}
## Tenant Idempotent Infrastructure Modules ## - Do not remove these - Danger zone end!



module "aws-s3" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-s3?ref=main"
    team_name = "demo-tenant2"
    app_name  = "my-python-app2"
}

module "aws-postgres" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-postgres?ref=main"
    team_name = "demo-tenant2"
    app_name  = "my-python-app2"
}

