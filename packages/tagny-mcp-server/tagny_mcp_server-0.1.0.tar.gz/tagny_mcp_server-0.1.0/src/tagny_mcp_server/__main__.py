"""main entry point"""

import typer

from tagny_mcp_server.config import mcp

# import tools to make them available
from tagny_mcp_server.web_access import fetch_page_links, fetch_url_text  # noqa: F401


def main(
    transport: str = "sse",
    host: str = "127.0.0.1",
    port: int = 8000,
    path: str = "/mcp",
):
    """launch mcp server with the same parameters as FastMCP.run() method
    such as

    Args:
        transport: Transport protocol to use ("stdio", "sse", or "streamable-http")
    """
    match transport:
        case "stdio":
            mcp.run(transport="stdio")  # Default, so transport argument is optional
        case "sse":
            mcp.run(transport, host=host, port=port)
        case "http":
            mcp.run(transport, host=host, port=port, path=path)


if __name__ == "__main__":
    typer.run(main)
