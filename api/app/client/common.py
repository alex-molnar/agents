
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
