import asyncio
from typing import Tuple, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

from .base import BaseFetcher
from metacrawl.config.settings import settings
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

class PlaywrightFetcher(BaseFetcher):
    def __init__(self, timeout_seconds: int = None, headless: bool = None):
        self.timeout_seconds = timeout_seconds or settings.playwright_timeout
        self.headless = headless if headless is not None else settings.headless

    async def fetch(self, url: str) -> Tuple[Optional[str], int, Optional[str], str]:
        logger.debug(f"Launching Playwright (headless={self.headless}) to fetch {url}")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(user_agent=settings.user_agent)
                page = await context.new_page()
                
                # Convert seconds to milliseconds for Playwright
                timeout_ms = self.timeout_seconds * 1000
                
                try:
                    response = await page.goto(
                        url, 
                        timeout=timeout_ms,
                        wait_until="domcontentloaded"
                    )
                    
                    if not response:
                        await browser.close()
                        return None, 500, "Playwright: No response received", url

                    # Playwright might still receive a non-200, but we assume
                    # we bypassed whatever blocked requests library.
                    status = response.status
                    final_url = page.url
                    html = await page.content()
                    
                    # For a standard fetch block simulation, return 200 on successful page load
                    if 200 <= status < 300 or status == 403:
                        # Sometimes headless browser returns 403 but page actually loads content via js
                        logger.info(f"Playwright successfully loaded {final_url}")
                        return html, 200, None, final_url
                    
                    logger.warning(f"Playwright fetched {final_url} but got status {status}")
                    return html, status, f"Playwright HTTP {status}", final_url

                finally:
                    await browser.close()

        except PlaywrightTimeoutError:
            logger.warning(f"Playwright timed out after {self.timeout_seconds}s fetching {url}")
            return None, 408, "Playwright timeout", url
        except Exception as e:
            logger.exception(f"Unexpected Playwright error fetching {url}: {e}")
            return None, 500, f"Playwright error: {str(e)}", url
