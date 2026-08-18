from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from logging import basicConfig, getLogger, INFO
from os import getenv

from app.client.local import available_models
from app.routers import agents, health
from app.middleware.logs import logging_endpoint
from uvicorn import run


app = FastAPI()
app.include_router(health.router)
app.include_router(agents.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
    allow_methods=getenv("CORS_ALLOW_METHODS", "*").split(","),
    allow_headers=getenv("CORS_ALLOW_HEADERS", "*").split(","),
)

app.middleware("http")(logging_endpoint)

log = getLogger(__name__)

basicConfig(
    level=getenv("LOG_LEVEL", INFO),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


@app.get("/models", status_code=200)
def get_models(response: Response):
    try:
        return available_models()
    except Exception as e:
        response.status_code = 500
        return {
            "error": str(e),
            "endpoint": "/models",
            "method": "GET"
        }

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)