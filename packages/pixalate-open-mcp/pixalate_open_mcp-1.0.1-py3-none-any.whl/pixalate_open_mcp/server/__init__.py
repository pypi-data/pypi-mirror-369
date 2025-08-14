from pixalate_open_mcp.models.config import load_config
from pixalate_open_mcp.server.app import create_mcp_server

server = create_mcp_server(load_config())

__all__ = ["create_mcp_server", "server"]
