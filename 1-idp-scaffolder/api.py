import schemas, utils
import cli
from fastapi import FastAPI, HTTPException

api = FastAPI(title="Scaffolder API", description="Scaffolding tools to create and deploy applications")

@api.get("/api/v1/cloud-service-templates")
async def get_cloud_service_templates():
    return [cloud_service_template.value for cloud_service_template in schemas.CloudServices]

@api.get("/api/v1/app-templates")
async def get_app_templates():
    return {"app_templates": utils.list_app_templates()}

@api.get("/api/v1/teams")
async def get_teams():
    return {"teams": utils.list_teams()}

@api.get("/api/v1/repos/{team_name}")
async def get_repos(team_name: str):
    return {"repos": utils.list_repos(team_name)}

@api.post("/api/v1/apps")
def generate_app(app: schemas.AppDetails):
    try:
        cli.generate_app_template(**app.model_dump(mode='json'))
        return {"message": "App generated successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        exc_name = e.__class__.__name__
        print(f"Error during app generation: {exc_name}: {e}")
        raise HTTPException(status_code=500, detail=f"{exc_name}: {e}")