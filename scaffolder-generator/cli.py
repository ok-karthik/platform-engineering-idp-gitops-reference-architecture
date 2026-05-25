import argparse
from pathlib import Path
from jinja2 import Template
import shutil
from binaryornot.check import is_binary

BASE_DIR = Path(__file__).resolve().parent
APP_TEMPLATE_DIR = BASE_DIR / "app-templates"
GITOPS_TEMPLATE_DIR = BASE_DIR / "gitops-template"
OUTPUT_DIR = BASE_DIR.parent / "generated-apps"

def _copy_and_render(source_dir, dest_dir, app_name, app_type, app_port):
    """Helper function to recursively copy files and render template fields."""
    try:
        for source_path in list(source_dir.rglob("*")):
            dest_path=dest_dir / source_path.relative_to(source_dir)
            if source_path.is_dir():
                dest_path.mkdir(parents=True, exist_ok=True)
            if source_path.is_file():
                # We know it's a file, still creating parent mkdir here for defensive programming
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                if not is_binary(str(source_path)):
                    print("Rendering file: ", source_path.relative_to(source_dir))
                    template_content = source_path.read_text()
                    rendered_content = Template(template_content).render(app_name=app_name, app_type=app_type, app_port=app_port)
                    dest_path.write_text(rendered_content)
                else:
                    print("Copying file: ", source_path.relative_to(source_dir))
                    shutil.copy2(source_path, dest_path)
        return True
    except Exception as e:
        print(f"Error copying/rendering {source_dir}: {e}")
        return False

def generate_app_template(app_name: str, app_type: str, app_port: int, source_app_template_dir: Path | None = None, source_gitops_template_dir: Path | None = None, dest_dir: Path | None = None) -> bool:
    if source_app_template_dir is None:
        source_app_template_dir = Path(APP_TEMPLATE_DIR) / app_type

    if source_gitops_template_dir is None:
        source_gitops_template_dir = Path(GITOPS_TEMPLATE_DIR)
    
    if dest_dir is None:
        dest_dir = Path(OUTPUT_DIR) / app_name

    if not source_app_template_dir.exists() or not source_gitops_template_dir.exists():
        print("Source directory does not exist: ", source_app_template_dir, source_gitops_template_dir)
        return False

    success_app_template = _copy_and_render(source_app_template_dir, dest_dir, app_name, app_type, app_port)
    success_gitops_template = _copy_and_render(source_gitops_template_dir, dest_dir, app_name, app_type, app_port)

    return success_app_template and success_gitops_template

def list_app_templates():
    return [template.name for template in Path(APP_TEMPLATE_DIR).iterdir() if template.is_dir()]

if __name__ == "__main__":
    parser=argparse.ArgumentParser(usage='%(prog)s -a <app-name> -t <app-type> -p <app-port>')
    parser.add_argument("-a","--app-name", help="    <app-name> - Name of the application to be generated", required=True)
    parser.add_argument("-t","--app-type", choices=list_app_templates(), help="    <app-type> - Type of the application to be generated", required=True)
    parser.add_argument("-p","--app-port", help="    <app-port> - Port of the application to be generated", required=True)
    args = parser.parse_args()

    generate_app_template(
        app_name=args.app_name,
        app_type=args.app_type,
        app_port=args.app_port
    )