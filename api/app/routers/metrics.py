
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


router = APIRouter(
    prefix="/metrics"
)


@router.get("/", status_code=200)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)