"""main entry point"""

import typer

from tagny_mcp_server import __version__
from tagny_mcp_server.config import mcp

# import tools to make them available
from tagny_mcp_server.web_access import (  # noqa: F401
    fetch_page_links,
    fetch_url_text,
    search_web_with_brave,
)


def main(
    transport: str = "sse",
    host: str = "127.0.0.1",
    port: int = 8000,
    path: str = "/mcp",
    version: bool = False,
):
    """launch mcp server with the same parameters as FastMCP.run() method
    such as

    Args:
        transport: Transport protocol to use ("stdio", "sse", or "streamable-http").
          Defaults to "sse".
        host (str, optional): host address. Defaults to "127.0.0.1".
        port (int, optional): port. Defaults to 8000.
        path (str, optional): path to serve the server at. Defaults to "/mcp".
        version (bool, optional): version of the package.
    """
    if version:
        print(__version__)
        return
    match transport:
        case "stdio":
            mcp.run(transport="stdio")  # Default, so transport argument is optional
        case "sse":
            mcp.run(transport, host=host, port=port)
        case "http":
            mcp.run(transport, host=host, port=port, path=path)


if __name__ == "__main__":
    typer.run(main)
