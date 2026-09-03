from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from logging import basicConfig, getLogger, INFO
from os import getenv

from app.fastapi.routers import agents, health
from app.client.local import available_models
from app.fastapi.routers import metrics
from app.fastapi.middleware.logs import logging_endpoint
from app.fastapi.middleware.metrics import metrics_middleware, startup_event
from uvicorn import run


api_app = FastAPI()

api_app.include_router(health.router)
api_app.include_router(agents.router)
api_app.include_router(metrics.router)

api_app.middleware("http")(logging_endpoint)
api_app.middleware("http")(metrics_middleware)
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
    allow_methods=getenv("CORS_ALLOW_METHODS", "*").split(","),
    allow_headers=getenv("CORS_ALLOW_HEADERS", "*").split(","),
)

api_app.on_event("startup")(startup_event) # TODO update this to non deprecated one

log = getLogger(__name__)

basicConfig(
    level=getenv("LOG_LEVEL", INFO),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


@api_app.get("/models", status_code=200)
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
    run(api_app, host="0.0.0.0", port=8000)
