locals = {
    resource_name_prefix = "team-a-app-b"
    tags = {
        Team        = "team-a"
        Service     = "app-b"
        ManagedBy   = "terraform"
        Owner       = "team-a"
    }
}

## Tenant Idempotent Infrastructure Modules ## - Do not remove these - Danger zone start!
module "aws-vpc" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-networking?ref=main"
    team_name = "team-a"
    app_name  = "app-b"
    vpc_cidr  = "10.0.0.0/16"
}

module "aws-iam" {
    source    = "git::https://github.com/ok-karthik/platform-engineering-idp-gitops-reference-architecture.git//templates/platform/cloud-services/aws-iam?ref=main"
    team_name = "team-a"
    app_name  = "app-b"
}
## Tenant Idempotent Infrastructure Modules ## - Do not remove these - Danger zone end!

