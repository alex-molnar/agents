from app.tools.get_temperature import GetTemperatureTool

tools = {
    
}

agents_registry = {
    'chatbot': tools.values()
}

def get_tools(agent: str | None = None):
    if agent is None:
        return tools.values()
    return [tools[tool_name] for tool_name in agents_registry.get(agent, []) if tool_name in tools]