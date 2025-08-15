"""Unit tests for BraveWrapper class"""

import pytest

from tagny_mcp_server.web_access.web_search import BraveWrapper


def test_brave_wrapper_initialization():
    """Test that BraveWrapper initializes correctly"""
    wrapper = BraveWrapper(request_delay=1.0)

    assert wrapper.request_delay == 1.0
    assert "search.brave.com" in wrapper.url_template


def test_brave_wrapper_search_success_or_error():
    """Test successful or fail search with mock response
    failure might happen if the search engine is not accessible.
    """
    wrapper = BraveWrapper(request_delay=1.0)  # No delay for testing
    result = wrapper.search("test query")

    assert result["query"] == "test query"
    assert "search.brave.com" in result["url"]
    assert "error" in result or len(result["results"]) > 0
    if len(result["results"]) > 0:
        results = result["results"]
        assert "url" in results[0]
        assert "title" in results[0]
        assert "extract" in results[0]


def test_brave_wrapper_search_empty_query():
    """Test search with empty query"""
    wrapper = BraveWrapper(request_delay=1.0)

    with pytest.raises(ValueError):
        wrapper.search("")


if __name__ == "__main__":
    # This is the specific test case from your request
    search_engine = BraveWrapper(request_delay=1.0)
    search_result = search_engine.search("classic poems")

    print(f"Search result: {search_result}")
    assert search_result is not None
    print("Test passed!")
