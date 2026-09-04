from logging import getLogger

from app.tools.common import Tool
from app.tools.mcp.mcp_config import get_mcp_tools


log = getLogger(__name__)


handwritten_tools: list[Tool] = [
]

tools: dict[str, Tool] = {tool.name: tool for tool in handwritten_tools + get_mcp_tools()}

agents_registry: dict[str, list[str]] = {
    'chatbot': list(tools.keys())
}

def get_tools(agent: str | None = None) -> list[Tool]:
    if agent is None:
        return list(tools.values())
    return [tools[tool_name] for tool_name in agents_registry.get(agent, []) if tool_name in tools]
