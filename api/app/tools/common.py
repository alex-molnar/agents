from dataclasses import dataclass
from multiprocessing.connection import Connection


@dataclass
class ToolParamProperties:
    type: str
    description: str

class Tool:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def call(self, _: dict, __: Connection):
        raise NotImplementedError()

    def get_paramproperties(self) -> dict[str, dict[str, str]]:
        raise NotImplementedError()

    def get_required(self) -> list[str]:
        raise NotImplementedError()

    def get_request_body(self) -> dict:
        return {
            'type': 'function',
            'function': {
                'name': self.name,
                'description': self.description,
                'parameters': {
                    'type': 'object',
                    'required': self.get_required(),
                    'properties': self.get_paramproperties()
                }
            }
        }