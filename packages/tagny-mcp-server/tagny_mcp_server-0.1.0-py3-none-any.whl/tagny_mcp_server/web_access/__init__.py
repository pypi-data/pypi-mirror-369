"""package for web access tools"""

from tagny_mcp_server.web_access.url_text_fetcher import (
    fetch_page_links,
    fetch_url_text,
)

__all__ = ["fetch_url_text", "fetch_page_links"]
