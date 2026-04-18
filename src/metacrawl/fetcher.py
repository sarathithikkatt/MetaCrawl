import aiohttp
import asyncio
from typing import Tuple, Optional
from .interfaces import FetcherABC

class AsyncFetcher(FetcherABC):
    def __init__(self, user_agent: str = "MetaCrawl/1.0", timeout_seconds: int = 15):
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds

    async def fetch(self, url: str) -> Tuple[Optional[str], int, Optional[str], str]:
        headers = {"User-Agent": self.user_agent}
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url, allow_redirects=True) as response:
                    status = response.status
                    final_url = str(response.url)
                    
                    if 200 <= status < 300:
                        # Success
                        html = await response.text()
                        return html, status, None, final_url
                    else:
                        # HTTP Error
                        return None, status, f"HTTP {status}: {response.reason}", final_url
        except asyncio.TimeoutError:
            return None, 408, "Request timed out", url
        except aiohttp.ClientError as e:
            return None, 500, f"Client error: {str(e)}", url
        except Exception as e:
            return None, 500, f"Unexpected error: {str(e)}", url
