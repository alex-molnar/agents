from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from time import time as now
import asyncio
import psutil

REQUEST_COUNT = Counter(
    'http_requests_total_api_agents', 
    'Total HTTP requests to agents.kak.im domain', 
    ['method', 'endpoint', 'status', 'agent', 'model']
)
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds_api_agents', 
    'HTTP request duration on agents.kak.im domain', 
    ['method', 'endpoint', 'agent', 'model']
)
CPU_USAGE = Gauge(
    'system_cpu_usage_percent', 
    'System CPU usage percentage'
)
MEMORY_USAGE = Gauge(
    'system_memory_usage_percent', 
    'System memory usage percentage'
)

async def metrics_middleware(request, call_next):
    start_time = now()
    
    response = await call_next(request)

    if request.url.path.startswith("/metrics"):
        return response

    if request.url.path.startswith("/agents"):
        agent = request.url.path.split("/")[2] if len(request.url.path.split("/")) > 2 else "N/A"
        model = request.query_params.get("model", "N/A")
    else:
        agent = "N/A"
        model = "N/A"
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
        agent=agent,
        model=model
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path,
        agent=agent,
        model=model
    ).observe(now() - start_time)
    
    return response

async def startup_event():
    asyncio.create_task(update_system_metrics())

async def update_system_metrics():
    while True:
        CPU_USAGE.set(psutil.cpu_percent())
        MEMORY_USAGE.set(psutil.virtual_memory().percent)
        await asyncio.sleep(5)