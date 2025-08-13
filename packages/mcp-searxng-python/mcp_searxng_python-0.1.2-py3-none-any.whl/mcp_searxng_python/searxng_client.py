"""
SearXNG client for web search with proxy support
"""
import json
import os
from typing import Dict, List, Optional, Any
import httpx
import logging

logger = logging.getLogger(__name__)

class SearXNGClient:
    """SearXNG client with proxy support"""

    def __init__(self):
        self.searxng_url = os.environ.get("SEARXNG_URL", "https://searx.be")
        self.proxy_type = os.environ.get("PROXY_TYPE")
        self.proxy_host = os.environ.get("PROXY_HOST")
        self.proxy_port = os.environ.get("PROXY_PORT")
        self.proxy_url = os.environ.get("PROXY_URL")

        # Configure proxy
        self.proxies = self._configure_proxy()

    def _configure_proxy(self) -> Optional[Dict[str, str]]:
        """Configure proxy settings"""
        if self.proxy_url:
            return {"http://": self.proxy_url, "https://": self.proxy_url}

        if self.proxy_type and self.proxy_host and self.proxy_port:
            # 确保代理类型为小写，支持大小写不敏感
            proxy_type_lower = self.proxy_type.lower()
            proxy_url = f"{proxy_type_lower}://{self.proxy_host}:{self.proxy_port}"
            return {"http://": proxy_url, "https://": proxy_url}

        return None

    async def search(
        self,
        query: str,
        pageno: int = 1,
        time_range: Optional[str] = None,
        language: str = "all",
        safesearch: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform web search using SearXNG

        Args:
            query: Search query string
            pageno: Page number (starts at 1)
            time_range: Time filter ("day", "month", "year")
            language: Language code ("en", "fr", "de", etc.) or "all"
            safesearch: Safe search level (0: None, 1: Moderate, 2: Strict)

        Returns:
            Dictionary containing search results
        """
        try:
            # Prepare search parameters
            params = {
                "q": query,
                "format": "json",
                "pageno": pageno,
                "language": language
            }

            if time_range:
                params["time_range"] = time_range

            if safesearch is not None:
                params["safesearch"] = safesearch

            # Configure HTTP client
            client_kwargs = {"timeout": 30.0}
            # httpx uses 'proxy' parameter, not 'proxies'
            if self.proxy_url:
                client_kwargs["proxy"] = self.proxy_url
            elif self.proxies:
                # Use the first proxy URL if proxies dict is provided
                proxy_url = list(self.proxies.values())[0] if self.proxies else None
                if proxy_url:
                    client_kwargs["proxy"] = proxy_url

            async with httpx.AsyncClient(**client_kwargs) as client:
                # Make search request
                search_url = f"{self.searxng_url}/search"
                response = await client.get(search_url, params=params)
                response.raise_for_status()

                # Parse JSON response
                data = response.json()

                # Format results
                results = {
                    "query": query,
                    "number_of_results": len(data.get("results", [])),
                    "page": pageno,
                    "results": []
                }

                for result in data.get("results", []):
                    formatted_result = {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "engine": result.get("engine", ""),
                        "parsed_url": result.get("parsed_url", []),
                        "score": result.get("score", 0)
                    }

                    # Add optional fields if present
                    if "publishedDate" in result:
                        formatted_result["published_date"] = result["publishedDate"]
                    if "img_src" in result:
                        formatted_result["image_url"] = result["img_src"]

                    results["results"].append(formatted_result)

                # Add metadata
                if "infoboxes" in data:
                    results["infoboxes"] = data["infoboxes"]
                if "suggestions" in data:
                    results["suggestions"] = data["suggestions"]

                logger.info(f"Search completed: {len(results['results'])} results for '{query}'")
                return results

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during search: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Search failed: HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error during search: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise Exception("Invalid response format from SearXNG")
        except Exception as e:
            logger.error(f"Unexpected error during search: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")
