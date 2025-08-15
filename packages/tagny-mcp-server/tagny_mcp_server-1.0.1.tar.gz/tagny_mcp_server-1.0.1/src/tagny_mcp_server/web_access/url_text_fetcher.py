"""A module implementing tools to get data from web pages (e.g. text and URL links)"""

from typing import List

import requests
from bs4 import BeautifulSoup

from tagny_mcp_server.config import mcp


def extract_text_from_html(html_content):
    """
    Extracts plain text from HTML content, removing all HTML tags.

    Args:
        html_content (str): HTML content as string

    Returns:
        str: Plain text content
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text and clean it up
    text = soup.get_text()

    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = " ".join(chunk for chunk in chunks if chunk)

    return text


@mcp.tool()
def fetch_url_text(url: str) -> str:
    """Download all visible text from a URL.

    Args:
        url (str): URL to fetch and parse

    Returns:
        str: Plain text content
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return extract_text_from_html(response.text)
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None


@mcp.tool()
def fetch_page_links(url: str) -> List[str]:
    """Return a list of all links on the page."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return [a["href"] for a in soup.find_all("a", href=True)]
