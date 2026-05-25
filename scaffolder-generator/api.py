import cli
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from enum import Enum

api = FastAPI()

@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    raw_errors = exc.errors()
    formatted_errors = []
    for error in raw_errors:
        loc = [str(item) for item in error.get("loc", []) if item != "body"]
        field = " -> ".join(loc) if loc else "request"
        msg = error.get("msg", "Validation failed")
        input_val = error.get("input")
        
        if error.get("type") == "missing":
            formatted_errors.append(f"Missing required field: '{field}'")
        elif error.get("type") == "extra_forbidden":
            formatted_errors.append(f"Unexpected extra field '{field}' (provided value: '{input_val}')")
        else:
            formatted_errors.append(f"Invalid value for '{field}': {msg} (provided value: '{input_val}')")
            
    print("Request Validation Failed:\n" + "\n".join(f"  - {err}" for err in formatted_errors))
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": formatted_errors}
    )

templates = cli.list_app_templates()
AppType = Enum("AppType", {t: t for t in templates}, type=str)

# Validate the input details datatypes and ensure the data is sent via JSON body rather than URL parameters
class App(BaseModel):
    """App Model request body validations"""
    model_config = {
        "extra": "forbid"
    }
    app_name: str = Field(min_length=2, max_length=40, pattern=r"^[a-z0-9][-a-z0-9]*[a-z0-9]$", description="Name of the application to be generated")
    app_type: AppType
    app_port: int = Field(default=8080, ge=0, le=65535, description="Port number of the application to be generated")
    team_name: str = Field(min_length=2, max_length=40, pattern=r"^[a-z0-9][-a-z0-9]*[a-z0-9]$", description="Team/Tenant name of the application to be generated")
    
@api.get("/")
async def root():
    return {"app_templates": cli.list_app_templates()}

@api.post("/generate-app")
def generate_app(app: App):
    try:
        cli.generate_app_template(**app.model_dump())
        return {"message": "App generated successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        exc_name = e.__class__.__name__
        print(f"Error during app generation: {exc_name}: {e}")
        raise HTTPException(status_code=500, detail=f"{exc_name}: {e}")