import argparse
from pathlib import Path
from jinja2 import Template
import shutil
from binaryornot.check import is_binary
import logger, yaml

# Absolute path to the directory containing this script (e.g., ".../1-idp-scaffolder")
BASE_DIR: Path = Path(__file__).resolve().parent
# Target output directory (e.g., ".../2-tenant-workloads")
OUTPUT_DIR: Path = BASE_DIR.parent / "2-tenant-workloads"
DEFAULT_CLOUD_SERVICES = ["aws-vpc", "aws-iam"]

def list_app_templates() -> list[str]:
    """List all app templates"""
    return [template.name for template in Path(BASE_DIR / "templates/platform/app-source-repo-types").iterdir() if template.is_dir()]

def list_cloud_services() -> list[str]:
    """List all cloud services except the default ones, they get created by default"""
    return [template.name for template in Path(BASE_DIR / "templates/platform/cloud-services").iterdir() if template.is_dir() and template.name not in DEFAULT_CLOUD_SERVICES]

def _copy_and_render(source_dir: Path, dest_dir: Path, app_name: str, app_type: str, app_port: int, team_name: str, vpc_cidr: str, cloud_services: list[str] = list(), exclude_patterns: list[str] = None) -> bool:
    """Helper function to recursively copy files and render template fields

    Args:
        source_dir: Source directory to copy files from
        dest_dir: Destination directory to copy files to
        app_name: Name of the application to be generated
        app_type: Type of the application to be generated
        app_port: Port of the application to be generated
        team_name: Team/Tenant name
        cloud_services: List of cloud services to be included in the workload
        exclude_patterns: List of patterns to exclude from rendering
        
    Returns:
        True if the files were copied and rendered successfully, False otherwise
    """
    if exclude_patterns is None:
        exclude_patterns = []
    current_file = None
    try:
        for source_path in source_dir.rglob("*"):
            if source_path.is_dir():
                continue

            dest_path = dest_dir / source_path.relative_to(source_dir)
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if is_binary(str(source_path)):
                print("Copying binary file: ", source_path.relative_to(source_dir))
                shutil.copy2(source_path, dest_path)
                continue

            relative_file_path = str(source_path.relative_to(source_dir))
            current_file = relative_file_path
            should_render = not any(pat in relative_file_path for pat in exclude_patterns)

            if not should_render:
                print("Copying file without rendering: ", relative_file_path)
                shutil.copy2(source_path, dest_path)
                continue

            print("Rendering file: ", relative_file_path)
            template_content = source_path.read_text()
            rendered_content = Template(template_content).render(
                **locals()
            )
            dest_path.write_text(rendered_content)
        return True
    except Exception as e:
        err_msg = f"Error copying/rendering {current_file or source_dir}: {e}"
        print(err_msg)
        raise RuntimeError(err_msg) from e

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
    dest_app_repo = OUTPUT_DIR / team_name / "apps-source" / app_name
    dest_gitops_repo = OUTPUT_DIR / team_name / "gitops-repo" / "apps" / app_name
    dest_infra_repo = OUTPUT_DIR / team_name / "infra-repo"

    # Mappings defining (source_dir, dest_dir, exclude_patterns)
    mappings = [
        (
            BASE_DIR / "templates" / "platform" / "app-source-repo-common",
            dest_app_repo,
            []
        ),
        (
            BASE_DIR / "templates" / "platform" / "app-source-repo-types" / app_type,
            dest_app_repo,
            []
        ),
        (
            BASE_DIR / "templates" / "user" / "gitops-repo",
            dest_gitops_repo,
            ["templated-manifests/templates"]  # Exclude Helm template directories from Jinja2
        ),
        (
            BASE_DIR / "templates" / "user" / "infra-repo",
            dest_infra_repo,
            []
        )
    ]

    # Pre-flight validation
    for src, _, _ in mappings:
        if not src.exists():
            raise FileNotFoundError(f"Source directory does not exist: {src}")

    # VPC IP range creation
    registry_file = OUTPUT_DIR / "cloud_vpcs_allocated.yaml"
    if not registry_file.exists():
        with open(registry_file, "w") as f:
            yaml.safe_dump({team_name: "10.0.0.0/16"}, f)
    else:
        with open(registry_file, "r") as f:
            cloud_vpcs_allocated = yaml.safe_load(f) or {}

        # Get or allocate the VPC CIDR
        if team_name in cloud_vpcs_allocated:
            vpc_cidr = cloud_vpcs_allocated[team_name]
        if not (OUTPUT_DIR / team_name ).exists():
            # Determine the next available index (e.g. 10.1.0.0/16, 10.2.0.0/16, etc.)
            max_index = max([int(cidr.split(".")[1]) for cidr in cloud_vpcs_allocated.values()])
            next_index = max_index + 1
            vpc_cidr = f"10.{next_index}.0.0/16"
            
            # Save the new allocation
            cloud_vpcs_allocated[team_name] = vpc_cidr
            with open(registry_file, "w") as f:
                yaml.safe_dump(cloud_vpcs_allocated, f)

    print("Allocated VPC CIDR: ", vpc_cidr)

    # Copy and render mappings
    for src, dest, exclude in mappings:
        _copy_and_render(src, dest, app_name, app_type, app_port, team_name, vpc_cidr, cloud_services, exclude_patterns=exclude)

    # Relocate and rename the CD workflow to the shared GitOps repository root
    src_wf = dest_gitops_repo / ".github" / "workflows" / "cd.yaml"
    if src_wf.exists():
        dest_wf = dest_gitops_repo.parent.parent / ".github" / "workflows" / f"cd-{app_name}.yaml"
        dest_wf.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_wf), str(dest_wf))
        shutil.rmtree(str(dest_gitops_repo / ".github"))  # Clean up the empty nested folder

    return True

if __name__ == "__main__":
    """Main function to parse arguments and generate app template"""
    parser=argparse.ArgumentParser(usage='%(prog)s -a <app-name> -t <app-type> -p <app-port> -team <team-name> -services <cloud-services>')
    parser.add_argument("-a", "--app-name", help="    <app-name> - Name of the application to be generated", required=True, type=str)
    parser.add_argument("-t", "--app-type", choices=list_app_templates(), help="    <app-type> - Type of the application to be generated", required=True, type=str)
    parser.add_argument("-p", "--app-port", help="    <app-port> - Port of the application to be generated", required=True, type=int)
    parser.add_argument("-team", "--team-name", help="    <team-name> - Team/Tenant name", required=True, type=str)
    parser.add_argument("-services", "--cloud-services", help="    <cloud-services> - List of Cloud Services to be included in the workload", nargs='+', required=False, type=str)
    args = parser.parse_args()

    allowed_cloud_services = list_cloud_services()
    if args.cloud_services:
        for cs in args.cloud_services:
            if cs not in allowed_cloud_services:
                parser.error(
                    f"Error: Invalid Cloud service '{cs}'."
                    f"\nAllowed cloud services: {', '.join(allowed_cloud_services)}"
                )
                

    generate_app_template(
        app_name=args.app_name,
        app_type=args.app_type,
        app_port=args.app_port,
        team_name=args.team_name,
        cloud_services=args.cloud_services
    )