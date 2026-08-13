from requests import post, get
from json import loads 
from os import getenv

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
            return [m['name'] for m in response.json()['models']]

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