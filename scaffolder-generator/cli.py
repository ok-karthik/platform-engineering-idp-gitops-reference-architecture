from typing import Mapping
import argparse
from pathlib import Path
from jinja2 import Template
import shutil
from binaryornot.check import is_binary

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR.parent / "generated-apps"

def _copy_and_render(source_dir, dest_dir, app_name, app_type, app_port, team_name, exclude_patterns=None):
    """Helper function to recursively copy files and render template fields."""
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
                app_name=app_name, app_type=app_type, app_port=app_port, team_name=team_name
            )
            dest_path.write_text(rendered_content)
        return True
    except Exception as e:
        err_msg = f"Error copying/rendering {current_file or source_dir}: {e}"
        print(err_msg)
        raise RuntimeError(err_msg) from e

def generate_app_template(app_name: str, app_type: str, app_port: int, team_name: str) -> bool:
    dest_app_repo = OUTPUT_DIR / team_name / app_name / "app-repo"
    dest_gitops_repo = OUTPUT_DIR / team_name / app_name / "gitops-repo"

    # Mappings defining (source_dir, dest_dir, exclude_patterns)
    mappings = [
        (
            BASE_DIR / "templates" / "app-repo-common",
            dest_app_repo,
            []
        ),
        (
            BASE_DIR / "templates" / "app-repo-types" / app_type,
            dest_app_repo,
            []
        ),
        (
            BASE_DIR / "templates" / "gitops-repo",
            dest_gitops_repo,
            ["templated-manifests/templates"]  # Exclude Helm template directories from Jinja2
        )
    ]

    # Pre-flight validation
    for src, _, _ in mappings:
        if not src.exists():
            raise FileNotFoundError(f"Source directory does not exist: {src}")

    # Copy and render mappings
    for src, dest, exclude in mappings:
        _copy_and_render(src, dest, app_name, app_type, app_port, team_name, exclude_patterns=exclude)

    return True

def list_app_templates():
    return [template.name for template in Path(BASE_DIR / "templates/app-repo-types").iterdir() if template.is_dir()]

if __name__ == "__main__":
    parser=argparse.ArgumentParser(usage='%(prog)s -a <app-name> -at <app-type> -p <app-port> -t <team-name>')
    parser.add_argument("-a", "--app-name", help="    <app-name> - Name of the application to be generated", required=True)
    parser.add_argument("-t", "--app-type", choices=list_app_templates(), help="    <app-type> - Type of the application to be generated", required=True)
    parser.add_argument("-p", "--app-port", help="    <app-port> - Port of the application to be generated", required=True)
    parser.add_argument("-team", "--team-name", help="    <team-name> - Team/Tenant name", required=True)
    args = parser.parse_args()

    generate_app_template(
        app_name=args.app_name,
        app_type=args.app_type,
        app_port=args.app_port,
        team_name=args.team_name
    )