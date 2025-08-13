import logging
import os
import json
from typing import Any, List, Dict, Optional

from mcp.server.fastmcp import FastMCP

from .searxng_client import SearXNGClient
from .url_reader import URLReader

# Get project root directory path for log file path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LOG_FILE = os.path.join(ROOT_DIR, "mcp-searxng.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE)
    ],
)
logger = logging.getLogger("mcp-searxng")

# Initialize FastMCP server
mcp = FastMCP("mcp-searxng")

# Initialize clients
searxng_client = SearXNGClient()
url_reader = URLReader()

@mcp.tool()
async def searxng_web_search(
    query: str,
    pageno: int = 1,
    time_range: Optional[str] = None,
    language: str = "all",
    safesearch: Optional[int] = None
) -> str:
    """
    Search the web using SearXNG.

    Args:
        query (str): The search query. This string is passed to external search services.
        pageno (int, optional): Search page number, starts at 1 (default 1)
        time_range (str, optional): Filter results by time range - one of: "day", "month", "year" (default: none)
        language (str, optional): Language code for results (e.g., "en", "fr", "de") or "all" (default: "all")
        safesearch (int, optional): Safe search filter level (0: None, 1: Moderate, 2: Strict) (default: instance setting)

    Returns:
        str: JSON string containing search results
    """
    try:
        logger.info(f"Performing search: query='{query}', page={pageno}, time_range={time_range}, language={language}, safesearch={safesearch}")

        # Validate parameters
        if not query or not query.strip():
            return json.dumps({"error": "Query cannot be empty"})

        if pageno < 1:
            return json.dumps({"error": "Page number must be 1 or greater"})

        if time_range and time_range not in ["day", "month", "year"]:
            return json.dumps({"error": "time_range must be one of: day, month, year"})

        if safesearch is not None and safesearch not in [0, 1, 2]:
            return json.dumps({"error": "safesearch must be 0 (None), 1 (Moderate), or 2 (Strict)"})

        # Perform search
        results = await searxng_client.search(
            query=query.strip(),
            pageno=pageno,
            time_range=time_range,
            language=language,
            safesearch=safesearch
        )

        return json.dumps(results, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in searxng_web_search: {str(e)}")
        return json.dumps({"error": f"Search failed: {str(e)}"})

@mcp.tool()
async def web_url_read(url: str) -> str:
    """
    Read and convert the content from a URL to markdown.

    Args:
        url (str): The URL to fetch and process

    Returns:
        str: JSON string containing title, markdown content, and metadata
    """
    try:
        logger.info(f"Reading URL: {url}")

        # Validate URL
        if not url or not url.strip():
            return json.dumps({"error": "URL cannot be empty"})

        url = url.strip()

        # Basic URL validation
        if not (url.startswith("http://") or url.startswith("https://")):
            return json.dumps({"error": "URL must start with http:// or https://"})

        # Read URL content
        result = await url_reader.read_url(url)

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Error in web_url_read: {str(e)}")
        return json.dumps({"error": f"Failed to read URL: {str(e)}"})

async def run_sse():
    """Run SearXNG MCP server in SSE mode."""
    try:
        logger.info("Starting SearXNG MCP server with SSE transport")
        await mcp.run_sse_async()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")

async def run_streamable_http():
    """Run SearXNG MCP server in streamable HTTP mode."""
    try:
        logger.info("Starting SearXNG MCP server with streamable HTTP transport")
        await mcp.run_streamable_http_async()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")

def run_stdio():
    """Run SearXNG MCP server in stdio mode."""
    try:
        logger.info("Starting SearXNG MCP server with stdio transport")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")

def main():
    """主入口函数 - 默认stdio模式"""
    mcp.run()

if __name__ == "__main__":
    main()
