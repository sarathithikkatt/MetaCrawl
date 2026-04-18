import aiohttp
import asyncio
from typing import Tuple, Optional
from .base import BaseFetcher
from metacrawl.config.settings import settings
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

class HttpFetcher(BaseFetcher):
    def __init__(self, user_agent: str = None, timeout_seconds: int = None):
        self.user_agent = user_agent or settings.user_agent
        self.timeout_seconds = timeout_seconds or settings.timeout

    async def fetch(self, url: str) -> Tuple[Optional[str], int, Optional[str], str]:
        headers = {"User-Agent": self.user_agent}
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url, allow_redirects=True) as response:
                    status = response.status
                    final_url = str(response.url)
                    
                    if 200 <= status < 300:
                        logger.debug(f"Successfully fetched {final_url} (status: {status})")
                        html = await response.text()
                        return html, status, None, final_url
                    else:
                        logger.warning(f"HTTP Error {status} fetching {final_url}: {response.reason}")
                        return None, status, f"HTTP {status}: {response.reason}", final_url
        except asyncio.TimeoutError:
            logger.warning(f"Request timed out fetching {url} after {self.timeout_seconds}s")
            return None, 408, "Request timed out", url
        except aiohttp.ClientError as e:
            logger.error(f"Client error fetching {url}: {e}")
            return None, 500, f"Client error: {str(e)}", url
        except Exception as e:
            logger.exception(f"Unexpected error fetching {url}: {e}")
            return None, 500, f"Unexpected error: {str(e)}", url
