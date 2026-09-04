from json import load
from logging import getLogger
from os import getenv
from pathlib import Path

from app.tools.mcp.mcp_tool import McpServerConfig, McpTool, load_tools


log = getLogger(__name__)


CONFIG_PATH = Path(getenv('MCP_CONFIG_PATH', Path(__file__).parent / 'mcp_servers.json'))


def read_config(path: Path = CONFIG_PATH) -> list[McpServerConfig]:
    """Read the mcp_servers.json file where servers are pasted as urls or configs."""
    if not path.is_file():
        log.info(f'No MCP config found at {path}, running without MCP tools')
        return []

    with path.open() as f:
        raw = load(f)

    servers = raw.get('mcpServers', raw) if isinstance(raw, dict) else {}
    configs = []

    for name, config in servers.items():
        try:
            configs.append(McpServerConfig.parse(name, config))
        except (ValueError, TypeError) as e:
            log.warning(f'Ignoring invalid MCP server config {name}: {e}')

    return configs


def get_mcp_tools(path: Path = CONFIG_PATH) -> list[McpTool]:
    """All tools of all configured MCP servers, ready to hand to an agent."""
    return [tool for server in read_config(path) for tool in load_tools(server)]
