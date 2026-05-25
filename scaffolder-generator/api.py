import cli
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum

api = FastAPI()

templates = cli.list_app_templates()
AppType = Enum("AppType", {t: t for t in templates}, type=str)

# Validate the input details datatypes and ensure the data is sent via JSON body rather than URL parameters
class App(BaseModel):
    """App Model request body validations"""
    app_name: str = Field(min_length=2, max_length=40, pattern=r"^[a-z0-9][-a-z0-9]*[a-z0-9]$", description="Name of the application to be generated")
    app_type: AppType
    app_port: int = Field(default=8080, ge=0, le=65535, description="Port number of the application to be generated")

    
@api.get("/")
async def root():
    return {"app_templates": cli.list_app_templates()}

@api.post("/generate-app")
def generate_app(app: App):
    success = cli.generate_app_template(**app.model_dump())
    if success:
        return {"message": "App generated successfully"}
    else:
        raise HTTPException(status_code=400, detail= "App generation failed")