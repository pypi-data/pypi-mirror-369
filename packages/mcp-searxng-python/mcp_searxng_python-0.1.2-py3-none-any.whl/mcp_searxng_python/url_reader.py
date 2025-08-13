"""
URL content reader with markdown conversion
"""
import os
from typing import Dict, Any
import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import logging

logger = logging.getLogger(__name__)

class URLReader:
    """URL content reader with proxy support"""

    def __init__(self):
        self.proxy_type = os.environ.get("PROXY_TYPE")
        self.proxy_host = os.environ.get("PROXY_HOST")
        self.proxy_port = os.environ.get("PROXY_PORT")
        self.proxy_url = os.environ.get("PROXY_URL")

        # Configure proxy
        self.proxies = self._configure_proxy()

    def _configure_proxy(self) -> Dict[str, str] | None:
        """Configure proxy settings"""
        if self.proxy_url:
            return {"http://": self.proxy_url, "https://": self.proxy_url}

        if self.proxy_type and self.proxy_host and self.proxy_port:
            # 确保代理类型为小写，支持大小写不敏感
            proxy_type_lower = self.proxy_type.lower()
            proxy_url = f"{proxy_type_lower}://{self.proxy_host}:{self.proxy_port}"
            return {"http://": proxy_url, "https://": proxy_url}

        return None

    async def read_url(self, url: str) -> Dict[str, Any]:
        """
        Read and convert URL content to markdown

        Args:
            url: The URL to fetch and process

        Returns:
            Dictionary containing title, markdown content, and metadata
        """
        try:
            # Configure HTTP client
            client_kwargs = {
                "timeout": 30.0,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            }
            # httpx uses 'proxy' parameter, not 'proxies'
            if self.proxy_url:
                client_kwargs["proxy"] = self.proxy_url
            elif self.proxies:
                # Use the first proxy URL if proxies dict is provided
                proxy_url = list(self.proxies.values())[0] if self.proxies else None
                if proxy_url:
                    client_kwargs["proxy"] = proxy_url

            async with httpx.AsyncClient(**client_kwargs) as client:
                # Fetch the URL
                response = await client.get(url)
                response.raise_for_status()

                # Parse HTML content
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract title
                title = ""
                if soup.title:
                    title = soup.title.string.strip() if soup.title.string else ""

                # Remove script and style elements
                for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()

                # Extract main content
                # Try to find main content areas
                main_content = None
                for selector in ["main", "article", ".content", "#content", ".post", ".entry"]:
                    main_content = soup.select_one(selector)
                    if main_content:
                        break

                # If no main content found, use body
                if not main_content:
                    main_content = soup.find("body")

                if not main_content:
                    main_content = soup

                # Convert to markdown
                markdown_content = md(str(main_content), heading_style="ATX")

                # Clean up markdown (remove excessive whitespace)
                lines = markdown_content.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if line or (cleaned_lines and cleaned_lines[-1]):  # Keep line if not empty or if previous line was not empty
                        cleaned_lines.append(line)

                markdown_content = '\n'.join(cleaned_lines)

                # Extract metadata
                metadata = {
                    "url": url,
                    "title": title,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length": len(markdown_content),
                    "status_code": response.status_code
                }

                # Try to extract description from meta tags
                description = ""
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc and meta_desc.get("content"):
                    description = meta_desc["content"].strip()
                elif soup.find("meta", property="og:description"):
                    description = soup.find("meta", property="og:description")["content"].strip()

                if description:
                    metadata["description"] = description

                result = {
                    "title": title,
                    "content": markdown_content,
                    "metadata": metadata
                }

                logger.info(f"Successfully read URL: {url} ({len(markdown_content)} characters)")
                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error reading URL {url}: {e.response.status_code}")
            raise Exception(f"Failed to read URL: HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error reading URL {url}: {str(e)}")
            raise Exception(f"Failed to read URL: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error reading URL {url}: {str(e)}")
            raise Exception(f"Failed to read URL: {str(e)}")
