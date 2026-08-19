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