from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI(title="demo-python-app")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return "<h1>Hello from demo-python-app!</h1>"

@app.get("/healthz")
def healthz():
    return "OK"

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")