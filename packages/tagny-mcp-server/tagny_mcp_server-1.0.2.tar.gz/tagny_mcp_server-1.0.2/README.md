# tagny-mcp-server
An MCP server with web search, URL text fetching, and more tools to enhance locally served LLMs.

[![GitHub License](https://img.shields.io/github/license/tagny/tagny-mcp-server)](LICENSE)
[![GitHub Actions Workflow](https://github.com/tagny/tagny-mcp-server/actions/workflows/build.yml/badge.svg)](https://github.com/tagny/tagny-mcp-server/actions/workflows/build.yml)
[![PyPI Version](https://img.shields.io/pypi/v/tagny-mcp-server)](https://pypi.org/project/tagny-mcp-server/)
[![Code Quality](https://img.shields.io/badge/code%20quality-ruff-blue)](https://github.com/astral-sh/ruff)
[![Contributors](
https://img.shields.io/github/contributors/tagny/tagny-mcp-server)](https://github.com/tagny/tagny-mcp-server)

## Features

- Fetch plain text content from URLs
- Extract all links from a webpage
- Designed to work with locally served LLMs via MCP protocol

## Installation

* from source
```bash
uv pip install -e .

# with dev dependencies
uv sync
```
* from PyPI repository
```sh
pip install tagny-mcp-server
```

## Usage

Start the MCP server:

* from source code:
```sh
uv run -m tagny_mcp_server
```
* after proper installation:
  - as described in the pyproject.toml at `project.scripts`, you can run the with the default arguments :
```sh
tagny-mcp-server
```
  - customize the arguments by running like this for example:
```sh
# see the help
uv run -m tagny_mcp_server --help

# see the version
uv run -m tagny_mcp_server --version

# change the default port
uv run -m tagny_mcp_server --port 5002
```

The server will run using Server-Sent Events (SSE) transport.

## Tools

### `fetch_url_text`
Downloads and parses HTML content from a URL, returning only the visible text.

### `fetch_page_links`
Returns a list of all hyperlinks found on a webpage.

### `search_web_with_brave`
An MCP tool that performs web searches using Brave search engine

### `search_web_with_duckduckgo`
An MCP tool that performs web searches using DuckDuckGo

## Project Structure

- `src/tagny_mcp_server/__init__.py` - Main package initializer that exports the version
- `src/tagny_mcp_server/__main__.py` - Entry point that launches the MCP server with command-line arguments
- `src/tagny_mcp_server/__version__.py` - Contains the package version string
- `src/tagny_mcp_server/config.py` - Configures the FastMCP server instance with name, instructions, and version
- `src/tagny_mcp_server/web_access/__init__.py` - Package initializer for web access tools that exports URL text fetching functions
- `src/tagny_mcp_server/web_access/url_text_fetcher.py` - Implements tools for fetching URL text and extracting links from web pages
- `src/tagny_mcp_server/web_access/web_search.py` - Implements Brave and DuckDuckGo search tools
- `pyproject.toml` - Project metadata, dependencies, and build configuration
- `tests/scripts/client.py` - Example client script for testing the server
- `tests/test_web_access_tools.py` - Tests for the web access tools
- `.gitignore` - Git ignore rules
- `README.md` - Project documentation
- `LICENSE` - License information
- `CHANGELOG.md` - Release notes and version history
- `CONTRIBUTING.md` - Guidelines for contributing to the project
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `.python-version` - Python version specification
- `.bumpversion.toml` - Configuration for version bumping tool
- `.github/` - GitHub workflow and issue template files

## Dependencies

- `beautifulsoup4` - HTML parsing
- `fastmcp` - MCP server framework
- `requests` - HTTP requests

## Testing

Tests are located in `tests/` and can be run with pytest:

```bash
pytest
```

Example client usage is shown in `scripts/client.py`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on our code of conduct and the process for submitting pull requests.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes to this project.

## Code Quality

This project uses pre-commit hooks to maintain code quality. Install them with:

```bash
pre-commit install
```

The following tools are used:
- black (code formatting)
- flake8 (linting)
- isort (import sorting)
- detect-secrets (secret detection)
- ruff (linting and fixing)

For more information, see [.pre-commit-config.yaml](.pre-commit-config.yaml).

## CI/CD

This project uses GitHub Actions for continuous integration and deployment:

- [Build workflow](.github/workflows/build.yml) - runs tests and code quality checks
- [Publish to Docker Hub](.github/workflows/publish2docker.yml) - publishes the Docker image on release
- [Publish to PyPI](.github/workflows/publish2pypi.yml) - publishes to PyPI on release

For more information, see [.github/workflows](.github/workflows).

## Running with Docker

You can build and run the Docker container using the provided `Dockerfile`. To test locally, you can use [act](https://nektos.github.io/act/) following the instructions at [https://nektos.github.io/act/](https://nektos.github.io/act/).

```bash
# Build the Docker image
docker build -t tagny-mcp-server .

# Run the Docker container
docker run -p 8000:8000 tagny-mcp-server
```

This will start the MCP server inside a Docker container, accessible at `http://localhost:8000/sse`.

That you can integrate in a `mcp.json` file like this:
```json
{
  "mcpServers": {
    "tagny-mcp-server": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```
