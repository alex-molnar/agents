from logging import getLogger

from requests import get
from os import getenv


log = getLogger(__name__)



model_descriptions = {
    "gemma4:e4b": "Flagship model with 4b context window. Ideal for heavy tasks.",
    "mistral:7b": "Large model for bigger workloads. Expect more accurate answer but a bigger waiting time",
    "qwen3.5:4b": "Middle class model, up to date processing, with middle of the pack memory overhead.",
    "llama3.2:latest": "Ollama's own edge model. Should be ideal for small to medium tasks",
    "qwen2.5:3b": "Small edge model for quick and accurate responses",
    "minimax-m3:cloud": "Cloud model for quick and accurate responses, with vision",
    "gpt-oss:120b-cloud": "Open source model by OpenAI for chat responses",
    "gemma4:31b-cloud": "Large cloud model for bigger workloads. Expect more accurate answer but a bigger waiting time",
}


model_weights = {
    "gemma4:e4b": 5,
    "mistral:7b": 6,
    "qwen3.5:4b": 4,
    "llama3.2:latest": 8,
    "qwen2.5:3b": 7,
    "minimax-m3:cloud": 2,
    "gpt-oss:120b-cloud": 1,
    "gemma4:31b-cloud": 3,
}


OLLAMA_LOCAL_URL = getenv('OLLAMA_API_URL', 'http://localhost:11434/api/{path}')


def available_models():
    response = get(OLLAMA_LOCAL_URL.format(path='tags'))
    log.debug(f"Received response from {OLLAMA_LOCAL_URL.format(path='tags')}: {response.status_code} - {response.text}")
    if response.status_code == 200:
        return {
            "models": sorted([
                {
                    'name': m['name'], 
                    'displayName': m['name'].split(':')[0],
                    'thinking': 'thinking' in m.get('capabilities', []),
                    'tools_support': 'tools' in m.get('capabilities', []),
                    'vision_support': 'vision' in m.get('capabilities', []),
                    'allowed': 'remote_model' not in m,
                    'weight': model_weights.get(m['name'], 200000),
                } for m in response.json()['models']
            ], key=lambda x: x['weight']),
            "default": "qwen2.5:3b"
        }
    else:
        return f'Error fetching models: {response.status_code} - {response.text}'

def get_version():
    response = get(OLLAMA_LOCAL_URL.format(path='version'))
    log.debug(f"Received response from {OLLAMA_LOCAL_URL.format(path='version')}: {response.status_code} - {response.text}")
    if response.status_code == 200:
        return {
            "status": "up",
            "version": response.json()['version']
        }
    else:
        raise Exception(f'Error fetching version: {response.status_code} - {response.text}')
