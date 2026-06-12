import yaml
from pathlib import Path

# Absolute path to the directory containing this script (e.g., ".../1-idp-scaffolder")
BASE_DIR: Path = Path(__file__).resolve().parent
# Target output directory (e.g., ".../2-tenant-workloads")
OUTPUT_DIR: Path = BASE_DIR.parent / "2-tenant-workloads"
DEFAULT_CLOUD_SERVICES = ["aws-networking", "aws-iam"]
VPC_REGISTRY_FILE = OUTPUT_DIR / "cloud_vpcs_allocated.yaml"

def list_app_templates() -> list[str]:
    """List all app templates"""
    languages_dir = BASE_DIR / "templates" / "languages"
    if not languages_dir.exists():
        raise FileNotFoundError(f"Templates directory not found at: {languages_dir}")
    return [template.name for template in languages_dir.iterdir() if template.is_dir()]

def list_cloud_service_templates() -> list[str]:
    """List all cloud service templates except the default ones"""
    # Since these are now remote modules, we return the list of supported ones
    return ["aws-postgres", "aws-s3"]

def list_repos(team_name: str) -> list[str]:
    """List all repos under a team"""
    return [template.name for template in Path(OUTPUT_DIR / team_name).iterdir() if template.is_dir()]

def list_teams() -> list[str]:
    """List all teams"""
    return [template.name for template in Path(OUTPUT_DIR).iterdir() if template.is_dir()]

def get_or_allocate_vpc_cidr(team_name: str) -> str:
    """Gets the existing CIDR block for a team, or allocates the next available /16 range."""
    
    # 1. Load the existing allocations
    cloud_vpcs_allocated = {}
    if VPC_REGISTRY_FILE.exists() and VPC_REGISTRY_FILE.stat().st_size > 0:
        with open(VPC_REGISTRY_FILE, "r") as f:
            cloud_vpcs_allocated = yaml.safe_load(f) or {}

    # 2. Get or calculate allocation
    if team_name in cloud_vpcs_allocated:
        return cloud_vpcs_allocated[team_name]
    
    # Determine the next second octet (10.x.0.0/16)
    if cloud_vpcs_allocated:
        max_index = max([int(cidr.split(".")[1]) for cidr in cloud_vpcs_allocated.values()])
        next_index = max_index + 1
    else:
        next_index = 0  # Start at 10.0.0.0/16
        
    vpc_cidr = f"10.{next_index}.0.0/16"
    
    # 3. Save the new allocation back to the YAML file
    cloud_vpcs_allocated[team_name] = vpc_cidr
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(VPC_REGISTRY_FILE, "w") as f:
        yaml.safe_dump(cloud_vpcs_allocated, f)
        
    return vpc_cidr