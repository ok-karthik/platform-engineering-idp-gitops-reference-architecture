locals = {
    resource_name_prefix = "team-b-app-b"
    tags = {
        Team        = "team-b"
        Service     = "app-b"
        ManagedBy   = "terraform"
        Owner       = "team-b"
    }
}

## Tenant Idempotent Infrastructure Modules ## - Do not remove these - Danger zone start!
module "aws-vpc" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-networking?ref=main"
    team_name = "team-b"
    app_name  = "app-b"
    vpc_cidr  = "10.1.0.0/16"
}

module "aws-iam" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-iam?ref=main"
    team_name = "team-b"
    app_name  = "app-b"
}
## Tenant Idempotent Infrastructure Modules ## - Do not remove these - Danger zone end!



module "aws-postgres" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-postgres?ref=main"
    team_name = "team-b"
    app_name  = "app-b"
}

