from app.tools.common import Tool
from app.client.chat import streamed_chat_for_agent, tool_call_for_agent
from os import getenv
from json import loads
from types import SimpleNamespace
from app.model.response import LlmCall, Response, ToolCall, Job, response_object_hook

OLLAMA_LOCAL_URL = getenv('OLLAMA_API_URL', 'http://localhost:11434/api/{path}')

class Agent:
    def __init__(self, name: str, tools: list[Tool], streaming: bool = True):
        self.name = name
        self.tools = tools
        self.tool_descriptions = [t.get_request_body() for t in self.tools]
        self.streaming = streaming

    def call_tool(self, tool_call: ToolCall):
        tool: Tool = next((x for x in self.tools if x.name == tool_call.function.name), None)
        return {
            "role": "tool",
            "content": tool.call(tool_call.function.arguments) if tool else 'Tool could not be found',
            "tool_name": tool_call.function.name
        }

    def execute(self, prompt: str, model: str):
        tool_calls = []
        history = [{
            'role': 'user',
            'content': prompt
        }]
        for message in streamed_chat_for_agent(OLLAMA_LOCAL_URL, prompt, model, self.tool_descriptions):
            data: Response = loads(message, object_hook=response_object_hook)
            if data.message.tool_calls:
                tool_calls.extend([Job(tool_call=tc) for tc in data.message.tool_calls])
                history.append(data.message.as_history())
            elif data.done and len(tool_calls) == 0:
                yield {'event': 'done'}
            else:
                yield {'event': 'message', 'data': data.message.content}

        yield from self.agent_loop(prompt, model, history=history, jobs=tool_calls + [Job(llm_call=LlmCall(url=OLLAMA_LOCAL_URL, tool_descriptions=self.tool_descriptions))])

    def agent_loop(self, prompt: str, model: str, history: list[dict], jobs: list[Job]):
        while jobs:
            job = jobs.pop(0)
            if job.tool_call:
                tool_call = job.tool_call
                yield {'event': 'tool_call', 'data': {'name': tool_call.function.name, 'args': tool_call.function.arguments}}
                result = self.call_tool(tool_call)
                history.append(result)
                yield {'event': 'tool_result', 'data': result}
            else:
                llm_call = job.llm_call
                yield {'event': 'llm_call', 'data': llm_call.url}
                tool_requested = False
                for message in tool_call_for_agent(llm_call.url, llm_call.tool_descriptions, history=history):
                    data: Response = loads(message, object_hook=response_object_hook)
                    if data.message.tool_calls:
                        tool_requested = True
                        for tool_call in data.message.tool_calls:
                            jobs.append(Job(tool_call=tool_call))
                            history.append(data.message.as_history())
                    elif data.done:
                        if tool_requested:
                            jobs.append(Job(llm_call=llm_call))
                        yield {'event': 'done'}
                    else:
                        yield {'event': 'message', 'data': data.message.content}



    # def execute(self, prompt: str, model: str):
    #     history = []
    #     tool_needed = True
    #     first = True
    #     while tool_needed:
    #         tool_needed = False
    #         gen = streamed_chat_for_agent(OLLAMA_LOCAL_URL, prompt, model, self.tool_descriptions, history=history) if first else tool_call_for_agent(OLLAMA_LOCAL_URL, self.tool_descriptions, history=history)
    #         for message in gen:
    #             data: Response = loads(message, object_hook=response_object_hook)
    #             if data.message.tool_calls:
    #                 for tool_call in data.message.tool_calls:
    #                     if len(history) == 0:
    #                         print("here")
    #                         history.append({
    #                             'role': 'user',
    #                             'content': prompt
    #                         })
    #                     tool_needed = True
    #                     history.append(self.call_tool(tool_call))
    #                     yield "Calling tool: " + tool_call.function.name
    #             elif data.done:
    #                 yield "Done"
    #             else:
    #                 yield data.message.content
    #         first = False


if __name__ == '__main__':
    from app.tools.get_temparature import GetTemperatureTool
    a = Agent('temp getting agent', [GetTemperatureTool()])
    for output in a.execute("What is the temparature in Budapest and London?", 'qwen2.5:3b'):
        if output['event'] == 'message':
            print(output['data'], end='')
        else:
            print(output)
    # a.execute("What is your name", 'qwen2.5:3b')
