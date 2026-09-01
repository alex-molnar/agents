from app.tools.common import Tool
from multiprocessing.connection import Connection

class GetTemperatureTool(Tool):
    def __init__(self):
        super().__init__("get_temparature", "Get the current temperature for a specified city.")

    def get_paramproperties(self) -> dict[str, dict[str, str]]:
        return {
            'city': {
                'type': 'string',
                'description': 'The name of the city to get the temperature for.'
            }
        }

    def get_required(self) -> list[str]:
        return ['city']

    def call(self, arguments: dict, pipe: Connection):
        city = arguments.get('city')
        result = self.get_temparature(city)
        pipe.send(result)
        pipe.close()

    def get_temparature(self, city: str):
        if city == 'London':
            return '17 degrees'
        elif city == 'Budapest':
            return '30 degrees'
        else:
            return 'it is literally impossible to determine temparature for this city'