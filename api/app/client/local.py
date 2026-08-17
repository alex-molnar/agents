from requests import post, get
from json import loads, dumps
from os import getenv

model_descriptions = {
    "gemma4:e4b": "Flagship model with 4b context window. Ideal for heavy tasks.",
    "mistral:7b": "Large model for bigger workloads. Expect more accurate anserw but a bigger waiting time",
    "qwen3.5:4b": "Middle class model, up to date processing, with middle of the pack memory overhead.",
    "phi3:mini": "Mini model. Ideal for quick small tasks",
    "llama3.2:latest": "Ollama's own edge model. Should be ideal for small to medium tasks",
    "qwen2.5:3b": "Small edge model for quick and accurate responses"
}

class Client:
    def __init__(self):
        self.url = getenv('OLLAMA_API_URL', 'http://localhost:11434/api/{path}')

    def __get_req(self, prompt: str, model: str = "qwen2.5:3b", history: list = [], tools: list = []):
        return {
            "model": model,
            "messages": history + [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "tools": tools,
            "stream": True
        }

    def get_models(self):
        response = get(self.url.format(path='tags'))
        if response.status_code == 200:
            print(dumps(response.json()['models'], indent=2))
            for m in response.json()['models']:
                print(m)
                print('capabilities' in m)
            return {
                "models": [
                    {
                        'name': m['name'], 
                        'displayName': m['name'].split(':')[0],
                        'thinking': 'thinking' in m.get('capabilities', []),
                        'tools_support': 'tools' in m.get('capabilities', []),
                        'allowed': True
                    } for m in response.json()['models']
                ] + [{
                    'name': 'gpt-5.1:latest',
                    'displayName': 'GPT 5.1 Cloud',
                    'thinking': True,
                    'tools_support': True,
                    'allowed': False
                }],
                "default": "qwen2.5:3b"
            }

    def get_version(self):
        response = get(self.url.format(path='version'))
        if response.status_code == 200:
            return {
                "status": "up",
                "ollama": {
                    "status": "up",
                    "version": response.json()['version']
                },
            }

    def send_request(self, prompt: str, model: str = "qwen2.5:3b"):
        response = post(self.url.format(path='chat'), json=self.__get_req(prompt, model), stream=True)
        response_text = ''
        for line in response.iter_lines():
            if line:
                data = loads(line.decode('utf-8'))
                response_text += data['message']['content']
        return {
            "status": "success",
            "response": response_text
        }

    def streamed_chat(self, prompt: str, model: str = "qwen2.5:3b"):
        response = post(self.url.format(path='chat'), json=self.__get_req(prompt, model), stream=True)
        for line in response.iter_lines():
            if line:
                data = loads(line.decode('utf-8'))
                if data['done'] == True:
                    yield f"event: end\ndata: {dumps({'message': 'done'})}\n\n"
                else:
                    yield f"event: message\ndata: {dumps({'message': data['message']['content']})}\n\n"