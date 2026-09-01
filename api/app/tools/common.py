from dataclasses import dataclass
from multiprocessing.connection import Connection

def create_param(name: str, description: str, type: str = 'string', required: bool = False):
    return {
        'name': name,
        'description': description,
        'type': type,
        'required': required
    }

def from_parameterlist(parameters: list[dict]):
    required = list()
    properties = {}
    for parameter in parameters:
        if parameter['required']:
            required.append(parameter['name'])
        properties[parameter['name']] = {
            'type': parameter['type'],
            'description': parameter['description']
        }
    return required, properties

def get_tool_request_body(name: str, description: str, parameters: list[dict] = [], type: str = 'function'):
    required, properties = from_parameterlist(parameters)
    return {
        'type': type,
        type: {
            'name': name,
            'description': description,
            'parameters': {
                'type': 'object',
                'required': required,
                'properties': properties
            }
        }
    }

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