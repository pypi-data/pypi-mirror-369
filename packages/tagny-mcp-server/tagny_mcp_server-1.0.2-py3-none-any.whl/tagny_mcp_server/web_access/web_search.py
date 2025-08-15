"""Web Search Engine Wrappers"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from tagny_mcp_server.config import mcp


class WebSearchEngineWrapper(ABC):
    """Abstract class reprsenting wrappers of search engines"""

    def __init__(self, url_template: str, request_delay: float = 1.0) -> None:
        """Constructor

        Args:
            url_template (str): the template URL expecting only the query.
            request_delay (float, optional): time to wait before each request to avoid
              overloading the search engine and being banned. in seconds.
              Defaults to 1.0.
        """
        self.url_template = url_template
        self.request_delay = request_delay

    @abstractmethod
    def extract_results(self, result_page_html: str) -> Dict[str, Any]:
        """Extract search results from a web search result page.

        Args:
            result_page_html (str): the HTML code content of a web search result page.

        Returns:
            Dict[str, Any]: a dictionary with the submitted query, requested URL, and
              received title, url, and extract for each result for each result,
              and an optional error message in case of failure.
        """
        raise NotImplementedError("Subclasses must implement extract_results()")

    def search(self, query: str) -> Dict[str, Any]:
        """Perform a search on the search engine

        Args:
            query (str): The search query

        Returns:
            Dict[str, Any]: output of the extract_results() method
        """
        query = query.strip()
        if len(query) == 0:
            raise ValueError("Query cannot be empty")
        # Wait before request
        print(f"Waiting {self.request_delay} second...")
        time.sleep(self.request_delay)

        # Encode the query for URL
        encoded_query = quote(query)

        # Brave Search URL
        search_url = self.url_template.format(encoded_query=encoded_query)

        # Headers to mimic a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp"
            ",*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        try:
            # Send the request
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse results as search engines don't provide structured JSON
            return {
                "query": query,
                "url": search_url,
                "results": self.extract_results(response.text),
            }

        except requests.exceptions.RequestException as e:
            print(f"Error fetching results: {e}")
            return {
                "query": query,
                "url": search_url,
                "error": f"Error fetching results: {e}",
            }


class BraveWrapper(WebSearchEngineWrapper):
    """Wrapper for Brave search engine."""

    def __init__(self, request_delay: float = 1.0) -> None:
        """Constructor

        Args:
            request_delay (float, optional): time to wait before each request to avoid
              overloading the search engine and being banned. in seconds.
              Defaults to 1.0.
        """
        url_template = "https://search.brave.com/search?q={encoded_query}&offset=0"
        super().__init__(url_template, request_delay)

    def extract_results(self, result_page_html: str) -> List[Dict[str, str]]:
        """extract result from Brave search result page based on HTML element classes
        and ids.

        Args:
            result_page_html (str): the HTML code content of a web search result page.

        Returns:
            Dict[str:str]: a dictionary with title, url, and snippet
               data for each result.
        """
        soup = BeautifulSoup(result_page_html, "html.parser")

        # Find divs with exactly the target classes and data-type="web"
        search_results = []

        # Search for div elements with specific class pattern
        div_elements = soup.find_all("div", attrs={"data-type": "web"})

        for div in div_elements:
            # Check if it has the exact class pattern
            class_attr = div.get("class", [])

            # Check if exactly 2 classes: "snippet" and "svelte-1o29vmf"
            if len(class_attr) == 2:
                if class_attr[0] == "snippet" and "svelte-1o29vmf" in class_attr[1]:
                    # Extract URL from anchor tag
                    anchor = div.find("a")
                    a_result_url = None
                    if anchor and anchor.get("href"):
                        a_result_url = anchor["href"]

                    # Extract title
                    title_div = div.find("div", class_="title")
                    a_result_title = None
                    if title_div:
                        a_result_title = title_div.get("title") or title_div.get_text(
                            strip=True
                        )

                    # Extract snippet content
                    snippet_content_div = div.find("div", class_="snippet-content")
                    a_result_extract = None
                    if snippet_content_div:
                        desc_div = snippet_content_div.find(
                            "div", class_="snippet-description"
                        )
                        if desc_div:
                            a_result_extract = desc_div.get_text(strip=True)

                    search_results.append(
                        {
                            "url": a_result_url,
                            "title": a_result_title,
                            "extract": a_result_extract,
                        }
                    )

        return search_results


@mcp.tool
def search_web_with_brave(query: str) -> Dict[str, Any]:
    """MCP tool that launch search with Brave"""
    engine = BraveWrapper(request_delay=1.0)
    return engine.search(query)


@mcp.tool
def search_web_with_duckduckgo(query: str, max_results: int = 5) -> Dict[str, Any]:
    """MCP tool that launch search with DuckDuckGo"""
    try:
        results = DDGS().text(query, max_results=max_results)
        return {"query": query, "results": results}
    except requests.exceptions.RequestException as ex:
        return {"query": query, "error": f"Error fetching results: {ex}"}
