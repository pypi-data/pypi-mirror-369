"""Common config module to make the same server accessible in sub-modules
and allow us to add tools"""

from fastmcp import FastMCP

from tagny_mcp_server import __version__

mcp = FastMCP(
    name="Tagny's MCP Servers",
    instructions="web search, URL text fetching, and more tools to enhance locally"
    " served LLMs",
    version=__version__,
)
