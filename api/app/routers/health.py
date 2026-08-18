
from fastapi import APIRouter, Response

from app.client.local import available_models, get_version


router = APIRouter(
    prefix="/health"
)


services = {
    'ollama': get_version
    # TODO more, eg: 'redis': check_redis_health
}


@router.get("/", status_code=200)
def health_check(fail_on_unavailable: bool = False, response: Response = None):
    health_status = {"status": "up"}
    for service_name, check_function in services.items():
        try:
            service_status = check_function()
            health_status[service_name] = service_status
        except Exception as e:
            if fail_on_unavailable:
                health_status["status"] = "down"
                response.status_code = 503
            health_status[service_name] = {
                "status": "down",
                "error": str(e)
            }
    return health_status

@router.get("/{service}", status_code=200)
def service_health_check(service: str, response: Response):
    if service not in services:
        response.status_code = 404
        return {"error": f"Service '{service}' not found."}
    try:
        return services[service]()
    except Exception as e:
        response.status_code = 503
        return {
            "status": "down",
            "error": str(e)
        }
