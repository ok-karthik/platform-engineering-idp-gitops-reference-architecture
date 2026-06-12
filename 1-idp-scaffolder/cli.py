import typer, copier
from pathlib import Path
import shutil
import yaml
from typing import Annotated
import schemas, utils

from pydantic import ValidationError

# Absolute path to the directory containing this script (e.g., ".../1-idp-scaffolder")
BASE_DIR: Path = Path(__file__).resolve().parent
# Target output directory (e.g., ".../2-tenant-workloads")
OUTPUT_DIR: Path = BASE_DIR.parent / "2-tenant-workloads"
DEFAULT_CLOUD_SERVICES = ["aws-vpc", "aws-iam"]


def generate_app_template(app_name: str, app_type: str, app_port: int, team_name: str, cloud_services: list[str] = list()) -> bool:
    """Generate app template
    
    Args:
        app_name: Name of the application to be generated
        app_type: Type of the application to be generated
        app_port: Port of the application to be generated
        team_name: Team/Tenant name
        cloud_services: List of cloud services to be included in the workload
        
    Returns:
        True if the app template was generated successfully, False otherwise
    """
    # VPC IP range creation
    vpc_cidr = utils.get_or_allocate_vpc_cidr(team_name)
    print(f"Allocated VPC CIDR: {vpc_cidr}")

    # Pass 1: Generate the entire team workspace structure and common files
    copier.run_copy(
        str(BASE_DIR / "templates" / "project-common"),
        str(OUTPUT_DIR),
        data={
            "team_name": team_name,
            "tenant_name": team_name, # support both keys
            "app_name": app_name,
            "app_type": app_type,
            "app_port": app_port,
            "cloud_services": cloud_services,
            "vpc_cidr": vpc_cidr
        },
        overwrite=True,
        defaults=True
    )

    # Pass 2: Inject the language-specific files directly into the root of the app source folder
    copier.run_copy(
        str(BASE_DIR / "templates" / "languages" / app_type),
        str(OUTPUT_DIR / team_name / "apps-source" / app_name),
        data={
            "team_name": team_name,
            "tenant_name": team_name,
            "app_name": app_name,
            "app_port": app_port
        },
        overwrite=True,
        defaults=True
    )
    return True

app = typer.Typer()

@app.command()
def create(
    app_name: Annotated[str, typer.Option("--app-name", "-a", help="<app-name> - Name of the application to be generated")],
    app_type: Annotated[str, typer.Option("--app-type", "-t", help="<app-type> - Type of the application to be generated")],
    app_port: Annotated[int, typer.Option("--app-port", "-p", help="<app-port> - Port of the application to be generated")],
    team_name: Annotated[str, typer.Option("--team-name", "-team", help="<team-name> - Team/Tenant name")],
    cloud_services: Annotated[list[str], typer.Option("--cloud-services", "-cs", help="<cloud-services> - List of Cloud Services to be included in the workload")]=[]
) -> bool:
    try:
        validated_data = schemas.AppDetails(
            app_name=app_name,
            app_type=app_type,
            app_port=app_port,
            team_name=team_name,
            cloud_services=cloud_services
        )
    except ValidationError as e:
        typer.echo("Error: Validation failed.")
        print(e.errors())
        for error in e.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            typer.echo(f"  - {loc}: {error['msg']}")
        raise typer.Exit(code=1)

    generate_app_template(**validated_data.model_dump(mode="json"))