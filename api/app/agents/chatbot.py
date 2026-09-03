
from logging import getLogger
from os import getenv
from time import sleep
from app.agents.common import Agent
from app.tools.registry import get_tools


log = getLogger(__name__)


OLLAMA_LOCAL_URL = getenv('OLLAMA_API_URL', 'http://localhost:11434/api/{path}')
OLLAMA_REMOTE_URL = getenv('OLLAMA_REMOTE_API_URL', 'https://ollama.com/api/{path}')


local_models = ["gemma4:e4b", "mistral:7b", "qwen3.5:4b", "llama3.2:latest", "qwen2.5:3b"]


def chat(prompt: str, model: str = "qwen2.5:3b"):
    agent = Agent('chatbot', get_tools(), system_prompt="You are a regular chatbot, that should answer questions for the user.")
    if model in local_models:
        log.debug(f"Using local model {model} at {OLLAMA_LOCAL_URL}")
        for message in agent.execute(prompt, model):
            if message['event'] in ['message', 'end']:
                yield f'event: {message["event"]}\ndata: {message["data"]}\n\n'
    else:
        log.debug(f"Using remote model {model} is not allowed for non-registered users")
        sleep (1)
        for chunk in ["Remote model ", model, " is not", " allowed", " for", " non-registered", " users"]:
            yield f'event: message\ndata: {chunk}\n\n'
            sleep(0.5)
        sleep(1)
        yield f'event: end\ndata: \n\n'

