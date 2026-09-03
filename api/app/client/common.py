from requests import post
from logging import getLogger
from os import getenv


log = getLogger(__name__)


OLLAMA_LOCAL_URL = getenv('OLLAMA_API_URL', 'http://localhost:11434/api/{path}')
OLLAMA_REMOTE_URL = getenv('OLLAMA_REMOTE_API_URL', 'https://ollama.com/api/{path}')


local_models = ["gemma4:e4b", "mistral:7b", "qwen3.5:4b", "llama3.2:latest", "qwen2.5:3b"]


def get_req_body(prompt: str | None = None, model: str = "qwen2.5:3b", history: list = [], tools: list = []):
    return {
        "model": model,
        "messages": history + ([{"role": "user", "content": prompt}] if prompt else []),
        "tools": tools,
        "stream": True,
        "think": False  # TODO: think about thinking
    }

def get_req_body_for_prompt(prompt: str, model: str = "qwen2.5:3b", history: list = [], tools: list = []):
    return get_req_body(prompt=prompt, model=model, history=history, tools=tools)

def chat(prompt: str | None = None, model: str = "qwen2.5:3b", tools: list = [], history: list = []):
    body = get_req_body(prompt=prompt, model=model, tools=tools, history=history)
    url = OLLAMA_LOCAL_URL if model in local_models else OLLAMA_REMOTE_URL
    headers = {} if model in local_models else {"Authorization": f"Bearer {getenv('OLLAMA_API_KEY')}"}

    log.debug(f'Calling {url} for model {model} with body {body}')

    response = post(url.format(path='chat'), json=body, stream=True, headers=headers)

    if response.status_code != 200:
        log.warning(f"Error sending request to {url.format(path='chat')}: {response.status_code} - {response.text}")
        return {
            'event': 'failure',
            'message': f"Error sending request to {url.format(path='chat')}: {response.status_code} - {response.text}"
        }

    for line in response.iter_lines():
        if line:
            yield line.decode('utf-8')