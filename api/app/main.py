from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from logging import basicConfig, getLogger, INFO
from os import getenv
from dataclasses import dataclass

from starlette.responses import StreamingResponse
from app.client.local import available_models, get_version, send_request, streamed_chat
from uvicorn import run

app = FastAPI()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true",
    allow_methods=getenv("CORS_ALLOW_METHODS", "*").split(","),
    allow_headers=getenv("CORS_ALLOW_HEADERS", "*").split(","),
)

log = getLogger(__name__)

basicConfig(
    level=getenv("LOG_LEVEL", INFO),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)



@dataclass
class tmp:
    prompt: str
    model: str = "qwen2.5:3b"



def wrap(data, endpoint: str, method: str, response: Response, status_code: int = 500):
    if method == "GET":
        response.headers["Content-Type"] = "application/json"
    if type(data) == str:
        response.status_code = status_code
        log.debug(f'Responding with error for {method} {endpoint}: {data}')
        return {"error": data, "endpoint": endpoint, "method": method}
    else:
        log.debug(f'Responding with data for {method} {endpoint}: {data}')
        return data

def log_request(endpoint: str, method: str, kwargs: dict = {}, data = None):
    log.debug(f"Received request for {method} {endpoint} with parameters: {kwargs} and body: {data}")


@app.get("/health", status_code=200)
def health_check(response: Response):
    log_request(endpoint="/health", method="GET")
    return wrap({'status': 'up'}, endpoint="/health", method="GET", response=response)

@app.get("/readiness", status_code=200)
def readiness_check(response: Response):
    log_request(endpoint="/readiness", method="GET")
    return wrap(get_version(), endpoint="/readiness", method="GET", response=response, status_code=503)

@app.get("/models", status_code=200)
def get_models(response: Response):
    log_request(endpoint="/models", method="GET")
    return wrap(available_models(), endpoint="/models", method="GET", response=response)

@app.get("/chat", status_code=200)
def chat(input: tmp, response: Response):
    log_request(endpoint="/chat", method="GET", data=input)
    return wrap(send_request(input.prompt, input.model), endpoint="/chat", method="GET", response=response)

@app.get("/chat-stream/{prompt}", status_code=200)
def chat_stream(prompt: str):
    log_request(endpoint="/chat-stream", method="GET", data={"prompt": prompt})
    return StreamingResponse(
        streamed_chat(prompt, model="qwen2.5:3b"),
        media_type="text/event-stream"
    )

@app.get("/model/{model}/chat-stream/{prompt}", status_code=200)
def chat_stream(model: str, prompt: str):
    log_request(endpoint="/model/<model>/chat-stream/<prompt>", method="GET", data={"model": model, "prompt": prompt})
    return StreamingResponse(
        streamed_chat(prompt, model=model),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000)