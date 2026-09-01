from app.tools.common import Tool
from app.client.agent import chat_for_agent
from os import getenv
from json import loads
from app.model.response import Response, ToolCall, response_object_hook
from multiprocessing import Process, Queue
from multiprocessing.connection import Connection, Pipe

OLLAMA_LOCAL_URL = getenv('OLLAMA_API_URL', 'http://localhost:11434/api/{path}')

class AgentJob:
    def __init__(self, name: str, pipe: Connection):
        self.name = name
        self.pipe = pipe

class Agent:
    def __init__(self, name: str, tools: list[Tool], system_prompt: str = "", streaming: bool = True):
        self.name = name
        self.tools = tools
        self.tool_descriptions = [t.get_request_body() for t in self.tools]
        self.system_prompt = system_prompt
        self.streaming = streaming

        self.job_queue: Queue[AgentJob] = Queue()

    def call_tool(self, tool_call: ToolCall):
        tool: Tool = next((x for x in self.tools if x.name == tool_call.function.name), None)
        pipe_end, pipe_start = Pipe()
        if tool:
            p = Process(target=tool.call, args=(tool_call.function.arguments,pipe_start))
            p.start()
            self.job_queue.put(AgentJob(name=tool_call.function.name, pipe=pipe_end))
        else: 
            p = Process(target=lambda pipe: pipe.send('Tool could not be found'), args=(pipe_start,))
            p.start()
            self.job_queue.put(AgentJob(name=tool_call.function.name, pipe=pipe_end))

    def execute(self, prompt: str, model: str):
        executable_prompt: str | bool = self.system_prompt + "\n" + prompt

        history = []

        while executable_prompt:
            used_prompt = executable_prompt if type(executable_prompt) == str else None
            executable_prompt = False

            for message in chat_for_agent(OLLAMA_LOCAL_URL, used_prompt, model, self.tool_descriptions, history):
                data: Response = loads(message, object_hook=response_object_hook)
                if data.message.tool_calls:
                    executable_prompt = True
                    for tc in data.message.tool_calls:
                        self.call_tool(tc)
                elif data.done and self.job_queue.empty():
                    yield {'event': 'prompt_finished'}
                else:
                    yield {'event': 'message', 'data': data.message.content}
    
            while not self.job_queue.empty():
                job = self.job_queue.get()
                yield {'event': 'tool_call', 'name': job.name}
                try:
                    result = job.pipe.recv()
                    yield {'event': 'tool_result', 'name': job.name, 'data': result}

                    if len(history) == 0:
                        history.append({'role': 'user', 'content': self.system_prompt + "\n" + prompt})

                    history.append({'role': 'tool', 'tool_name': job.name, 'content': result})
                except EOFError as e:
                    yield {'event': 'tool_error', 'name': job.name, 'error': str(e)}

        yield {'event': 'finished'}

