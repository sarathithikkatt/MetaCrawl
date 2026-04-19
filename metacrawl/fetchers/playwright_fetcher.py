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
                # Launch with arguments to disable HTTP/2 and make the browser more robust.
                # Disabling HTTP/2 often fixes net::ERR_HTTP2_PROTOCOL_ERROR on certain sites.
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=[
                        "--disable-http2",
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                    ]
                )
                context = await browser.new_context(
                    user_agent=settings.user_agent,
                    viewport={"width": 1920, "height": 1080},
                    ignore_https_errors=True,
                    java_script_enabled=True,
                    locale="en-US",
                    timezone_id="America/New_York",
                )
                page = await context.new_page()
                
                # Further mask the automation footprint
                await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                # Convert seconds to milliseconds for Playwright
                timeout_ms = self.timeout_seconds * 1000
                
                try:
                    # Using 'domcontentloaded' is often enough and faster than 'load'
                    response = await page.goto(
                        url, 
                        timeout=timeout_ms,
                        wait_until="domcontentloaded"
                    )
                    
                    if not response:
                        # Even if response is None, we might have some content if the page started loading
                        html = await page.content()
                        if len(html) > 500: # Arbitrary threshold for "some content"
                            logger.info(f"Playwright: No response but found content ({len(html)} bytes)")
                            return html, 200, None, url
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

                except PlaywrightTimeoutError:
                    # On timeout, try to see if we have any content already
                    logger.warning(f"Playwright timed out after {self.timeout_seconds}s fetching {url}. Attempting to retrieve partial content.")
                    try:
                        html = await page.content()
                        if len(html) > 500:
                            logger.info(f"Playwright: Recovered content after timeout ({len(html)} bytes)")
                            return html, 200, None, url
                    except:
                        pass
                    return None, 408, "Playwright timeout", url
                finally:
                    await browser.close()

        except Exception as e:
            logger.exception(f"Unexpected Playwright error fetching {url}: {e}")
            return None, 500, f"Playwright error: {str(e)}", url
