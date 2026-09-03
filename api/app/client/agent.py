from requests import post
from logging import getLogger

from app.client.common import get_req_body


log = getLogger(__name__)


def chat_for_agent(url: str, prompt: str | None = None, model: str = "qwen2.5:3b", tools: list = [], history: list = []):
    body = get_req_body(prompt=prompt, model=model, tools=tools, history=history)
    log.debug(f'Calling chat API with body: {body}')
    response = post(url.format(path='chat'), json=body, stream=True)

    if response.status_code != 200:
        log.warning(f"Error sending request to {url.format(path='chat')}: {response.status_code} - {response.text}")
        return {
            'event': 'failure',
            'message': f"Error sending request to {url.format(path='chat')}: {response.status_code} - {response.text}"
        }

    for line in response.iter_lines():
        if line:
            yield line.decode('utf-8')