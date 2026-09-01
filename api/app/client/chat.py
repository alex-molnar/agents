from logging import getLogger
from requests import post
from json import loads, dumps


log = getLogger(__name__)


def __get_req_body(prompt: str, model: str = "qwen2.5:3b", history: list = [], tools: list = []):
    return {
        "model": model,
        "messages": history + [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "tools": tools,
        "stream": True,
        "think": False  # TODO: think about thinking
    }

def streamed_chat(url: str, prompt: str, model: str):
    response = post(url.format(path='chat'), json=__get_req_body(prompt, model=model, history=[], tools=[]), stream=True)
    if response.status_code != 200:
        log.warning(f"Error sending request to {url.format(path='chat')}: {response.status_code} - {response.text}")
        return f"Error sending request: {response.status_code} - {response.text}"
    for line in response.iter_lines():
        if line:
            data = loads(line.decode('utf-8'))
            if data['done'] == True:
                yield f"event: end\ndata: {dumps({'message': 'done'})}\n\n"
            else:
                yield f"event: message\ndata: {dumps({'message': data['message']['content']})}\n\n"
