from logging import getLogger
from json import dumps

log = getLogger(__name__)

async def logging_endpoint(request, call_next):
    log.info(f"Request received on {request.method} {request.url.path} with params: {request.query_params} body: {await request.body()} and headers: {dumps(dict(request.headers))}")
    response = await call_next(request)
    log.info(f"Responding on {request.method} {request.url.path} with status {response.status_code} and headers: {dumps(dict(response.headers))}")
    return response