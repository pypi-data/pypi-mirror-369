"""a module implementing a fastMCP client to test if the MCP server is started
and if the MCP server's tools are working as expected"""

import pytest
from fastmcp.client import Client

SSE_URL = "http://localhost:8000/sse"
client = Client(SSE_URL)


@pytest.mark.asyncio
async def test_list_tools():
    """test that the list of tools if complete"""
    # Connection is established here
    async with client:
        print(f"Client connected: {client.is_connected()}")

        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        assert len(tools) > 0


@pytest.mark.asyncio
async def test_fetch_url_text():
    """test that the list of tools if complete"""
    # Connection is established here
    async with client:
        print(f"Client connected: {client.is_connected()}")

        tools = await client.list_tools()
        if any(tool.name == "fetch_url_text" for tool in tools):
            result = await client.call_tool(
                "fetch_url_text",
                {
                    "url": "https://apidog.com/blog/fastmcp/",
                },
            )
            print(f"Greet result: {result.content[0].text[:500]} ...")
            assert result is not None
            assert len(result.content[0].text) > 0
