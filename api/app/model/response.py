

from dataclasses import dataclass, field

@dataclass
class Function:
    index: int
    name: str
    arguments: dict[str, str]

@dataclass
class ToolCall:
    id: str
    function: Function

    def as_history(self):
        return {
            'id': self.id,
            'function': {
                'index': self.function.index,
                'name': self.function.name,
                'arguments': self.function.arguments
            }
        }

@dataclass
class LlmCall:
    url: str
    tool_descriptions: list[dict]

@dataclass
class Job:
    tool_call: ToolCall | None = None
    llm_call: LlmCall | None = None

@dataclass
class Message:
    role: str
    content: str
    tool_calls: list[ToolCall] | None = None

    def as_history(self):
        if self.tool_calls:
            return {
                'role': self.role,
                'content': self.content,
                'tool_calls': [tc.as_history() for tc in self.tool_calls]
            }
        return {
            'role': self.role,
            'content': self.content
        }

@dataclass
class Response:
    model: str
    created_at: str
    message: Message
    done: bool
    done_reason: str | None = None
    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    prompt_eval_duration: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None


def response_object_hook(d: dict):
    """Convert nested dicts to appropriate dataclass instances."""
    # Check for Response fields
    if 'model' in d and 'created_at' in d and 'message' in d and 'done' in d:
        return Response(**d)
    # Check for Message fields
    if 'role' in d and 'content' in d:
        return Message(**d)
    # Check for ToolCall fields
    if 'id' in d and 'function' in d and isinstance(d.get('function'), (Function, dict)):
        return ToolCall(**d)
    # Check for Function fields
    if 'index' in d and 'name' in d and 'arguments' in d:
        return Function(**d)
    # Return dict as-is for other objects (like arguments dict)
    return d
