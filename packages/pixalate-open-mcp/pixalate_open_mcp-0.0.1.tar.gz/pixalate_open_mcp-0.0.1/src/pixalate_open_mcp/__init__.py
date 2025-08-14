import asyncio
import logging
import sys

from pixalate_open_mcp.server.app import create_mcp_server, server

__version__ = "0.1.0"
__all__ = ["create_mcp_server", "server"]


def main(transport: str = "stdio"):
    """Entry point for MCP server

    Args:
        transport: Transport mode to use ("sse" or "stdio")
    """
    try:
        logger = logging.getLogger(__name__)
        if transport == "stdio":
            asyncio.run(server.run_stdio_async())
        else:
            asyncio.run(server.run_sse_async())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
