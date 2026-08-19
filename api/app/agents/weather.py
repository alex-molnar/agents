
from logging import getLogger
from os import getenv
from json import dumps
from app.client.chat import streamed_chat2
from app.tools.get_temparature import get_temperature
from app.tools.common import get_tool_request_body, create_param


log = getLogger(__name__)


OLLAMA_LOCAL_URL = getenv('OLLAMA_API_URL', 'http://localhost:11434/api/{path}')
OLLAMA_REMOTE_URL = getenv('OLLAMA_REMOTE_API_URL', 'https://ollama.com/api/{path}')


local_models = ["gemma4:e4b", "mistral:7b", "qwen3.5:4b", "llama3.2:latest", "qwen2.5:3b"]


def ask_for_weather(prompt: str, model: str = "qwen2.5:3b"):
    if model in local_models:
        log.debug(f"Using local model {model} at {OLLAMA_LOCAL_URL}")
        for mess in streamed_chat2(OLLAMA_LOCAL_URL, prompt, model=model, tools=[get_tool_request_body('get_temperature', 'Get the temperature for a city', [create_param('city', 'Name of the city', 'string', True)])]):
            if mess['event'] == 'done':
                yield f"event: end\ndata: {dumps({'message': 'done'})}\n\n"
            elif 'tool_calls' in mess and len(mess['tool_calls']) > 0:
                for tool_call in mess['tool_calls']:
                    print(f'\n\n\n CALLING TOOL: {get_temperature(tool_call['arguments']['city'])}\n\n\n')
                yield f"event: message\ndata: {dumps({'message': ' - calling tool - '})}\n\n"
            else:
                yield f"event: message\ndata: {dumps({'message': mess['content']})}\n\n"
    else:
        log.debug(f"Using remote model {model} at {OLLAMA_REMOTE_URL}")
        return streamed_chat2(OLLAMA_REMOTE_URL, prompt, model=model)

