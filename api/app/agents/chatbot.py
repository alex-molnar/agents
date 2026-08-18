
from logging import getLogger
from os import getenv
from app.client.chat import streamed_chat


log = getLogger(__name__)


OLLAMA_LOCAL_URL = getenv('OLLAMA_API_URL', 'http://localhost:11434/api/{path}')
OLLAMA_REMOTE_URL = getenv('OLLAMA_REMOTE_API_URL', 'https://ollama.com/api/{path}')


local_models = ["gemma4:e4b", "mistral:7b", "qwen3.5:4b", "llama3.2:latest", "qwen2.5:3b"]


def chat(prompt: str, model: str = "qwen2.5:3b"):
    if model in local_models:
        log.debug(f"Using local model {model} at {OLLAMA_LOCAL_URL}")
        return streamed_chat(OLLAMA_LOCAL_URL, prompt, model=model)
    else:
        log.debug(f"Using remote model {model} at {OLLAMA_REMOTE_URL}")
        return streamed_chat(OLLAMA_REMOTE_URL, prompt, model=model)

