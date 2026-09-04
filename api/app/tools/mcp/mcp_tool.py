from asyncio import run, wait_for
from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass, field
from json import dumps
from logging import getLogger
from multiprocessing.connection import Connection
from os.path import expandvars
from typing import Any

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
from mcp.shared._httpx_utils import create_mcp_http_client
from mcp.types import CallToolResult, TextContent
from mcp.types import Tool as McpToolDefinition

from app.tools.common import Tool


log = getLogger(__name__)


DEFAULT_TIMEOUT_SECONDS = 60.0


def _expand(value: Any) -> Any:
    """Resolve $ENV_VAR / ${ENV_VAR} placeholders so configs can reference secrets."""
    if isinstance(value, str):
        return expandvars(value)
    if isinstance(value, dict):
        return {k: _expand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand(v) for v in value]
    return value


@dataclass
class McpServerConfig:
    """One MCP server, either remote (url) or local (command)."""

    name: str
    url: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    command: str | None = None
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    cwd: str | None = None
    timeout: float = DEFAULT_TIMEOUT_SECONDS
    enabled: bool = True

    def __post_init__(self):
        if not self.url and not self.command:
            raise ValueError(f"MCP server '{self.name}' needs either a 'url' or a 'command'")
        if self.url and self.command:
            raise ValueError(f"MCP server '{self.name}' cannot define both a 'url' and a 'command'")

    @staticmethod
    def parse(name: str, config: str | dict) -> 'McpServerConfig':
        """Accept a bare url string or a Claude/Cursor style server config object."""
        if isinstance(config, str):
            return McpServerConfig(name=name, url=_expand(config))

        config = _expand(config)
        return McpServerConfig(
            name=name,
            url=config.get('url') or config.get('serverUrl'),
            headers=config.get('headers', {}),
            command=config.get('command'),
            args=config.get('args', []),
            env=config.get('env', {}),
            cwd=config.get('cwd'),
            timeout=float(config.get('timeout', DEFAULT_TIMEOUT_SECONDS)),
            enabled=config.get('enabled', True),
        )

    def stdio_parameters(self) -> StdioServerParameters:
        return StdioServerParameters(command=self.command, args=self.args, env=self.env or None, cwd=self.cwd)


@asynccontextmanager
async def connect(server: McpServerConfig):
    """Open a session to the server, over HTTP for a url and over stdio for a command."""
    async with AsyncExitStack() as stack:
        if server.url:
            http_client = await stack.enter_async_context(create_mcp_http_client(headers=server.headers or None))
            transport = streamable_http_client(server.url, http_client=http_client)
        else:
            transport = stdio_client(server.stdio_parameters())

        yield await stack.enter_async_context(Client(transport, read_timeout_seconds=server.timeout))


def _render(result: CallToolResult) -> str:
    """Flatten an MCP tool result into the plain text the agent feeds back to the model."""
    texts = [block.text for block in result.content if isinstance(block, TextContent)]

    if not texts and result.structured_content is not None:
        texts = [dumps(result.structured_content)]

    if not texts:
        texts = [f'<{getattr(block, "type", "unknown")} content>' for block in result.content]

    rendered = '\n'.join(texts) if texts else 'Tool returned no content'
    return f'Tool reported an error: {rendered}' if result.is_error else rendered


class McpTool(Tool):
    """Exposes a single tool of an MCP server through the regular Tool interface.

    Every call opens its own session because the agent runs tools in a separate
    process, which cannot inherit a connection from the parent.
    """

    def __init__(self, server: McpServerConfig, definition: McpToolDefinition):
        super().__init__(
            name=f'{server.name}__{definition.name}',
            description=definition.description or f'{definition.name} (provided by MCP server {server.name})',
        )
        self.server = server
        self.remote_name = definition.name
        self.input_schema = definition.input_schema or {}

    def get_paramproperties(self) -> dict[str, dict[str, str]]:
        return self.input_schema.get('properties', {})

    def get_required(self) -> list[str]:
        return self.input_schema.get('required', [])

    async def _call(self, arguments: dict) -> str:
        async with connect(self.server) as client:
            result = await client.call_tool(self.remote_name, arguments or {})
        return _render(result)

    def call(self, arguments: dict, pipe: Connection):
        log.info(f'Calling MCP tool {self.name} with arguments {arguments}')
        try:
            pipe.send(run(wait_for(self._call(arguments), timeout=self.server.timeout)))
        except Exception as e:
            log.warning(f'MCP tool {self.name} failed: {e}')
            pipe.send(f'Tool {self.name} failed: {e}')
        finally:
            pipe.close()


async def _discover(server: McpServerConfig) -> list[McpToolDefinition]:
    async with connect(server) as client:
        return (await client.list_tools()).tools


def load_tools(server: McpServerConfig) -> list[McpTool]:
    """Connect once at startup to turn every tool of a server into an McpTool."""
    if not server.enabled:
        log.info(f'Skipping disabled MCP server {server.name}')
        return []

    try:
        definitions = run(wait_for(_discover(server), timeout=server.timeout))
    except Exception as e:
        log.warning(f'Could not list tools of MCP server {server.name}: {e}')
        return []

    tools = [McpTool(server, definition) for definition in definitions]
    log.info(f'Loaded {len(tools)} tools from MCP server {server.name}: {[t.name for t in tools]}')
    return tools
