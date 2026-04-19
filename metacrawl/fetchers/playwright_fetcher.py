from typing import Tuple, Optional
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

from .base import BaseFetcher
from metacrawl.config import settings
from metacrawl.utils import get_logger

from playwright_stealth import Stealth

logger = get_logger(__name__)


class PlaywrightFetcher(BaseFetcher):
    def __init__(self, timeout_seconds: int = None, headless: bool = None):
        self.timeout_seconds = timeout_seconds or settings.playwright_timeout
        self.headless = headless if headless is not None else settings.headless

    async def fetch(self, url: str) -> Tuple[Optional[str], int, Optional[str], str]:
        logger.debug(f"[Playwright] Starting fetch | URL={url} | headless={self.headless}")

        try:
            async with async_playwright() as p:
                logger.debug("[Playwright] Launching Chromium...")

                # browser = await p.chromium.launch(
                #     headless=self.headless,
                #     args=[
                #         "--headless=new",  # modern headless
                #         "--disable-http2",
                #         "--no-sandbox",
                #         "--disable-setuid-sandbox",
                #         "--disable-dev-shm-usage",
                #     ]
                # )

                browser = await p.chromium.launch(
                    headless=True,
                    channel="chrome",
                    args=[
                        "--headless=new",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ]
                )

                logger.debug("[Playwright] Creating browser context...")

                context = await browser.new_context(
                    user_agent=settings.user_agent,
                    viewport={"width": 1920, "height": 1080},
                    locale="en-US",
                    timezone_id="America/New_York",
                    extra_http_headers={
                        "Accept-Language": "en-US,en;q=0.9",
                        "Upgrade-Insecure-Requests": "1",
                        "DNT": "1",
                    },
                )

                page = await context.new_page()

                logger.debug("[Playwright] Applying stealth...")
                stealth = Stealth()
                await stealth.apply_stealth_async(page)

                timeout_ms = self.timeout_seconds * 1000

                try:
                    logger.debug(f"[Playwright] Navigating to {url} (timeout={timeout_ms}ms)")

                    response = await page.goto(
                        url,
                        timeout=timeout_ms,
                        wait_until="load"
                    )

                    # Small delay to allow JS rendering
                    await page.wait_for_timeout(1000)

                    if not response:
                        logger.warning("[Playwright] No response object received")

                        html = await page.content()
                        logger.debug(f"[Playwright] Content length={len(html)}")

                        if len(html) > 500:
                            logger.info("[Playwright] Partial content recovered despite no response")
                            return html, 200, None, url

                        await browser.close()
                        return None, 500, "Playwright: No response received", url

                    status = response.status
                    final_url = page.url
                    
                    headers = response.headers
                    content_type = headers.get("content-type", "").lower()
                    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                        logger.warning(f"[Playwright] Skipping non-HTML content type: {content_type} for {final_url}")
                        await browser.close()
                        return None, 415, f"Unsupported Content-Type: {content_type}", final_url

                    logger.debug(f"[Playwright] Response status={status} | final_url={final_url}")

                    html = await page.content()
                    logger.debug(f"[Playwright] HTML size={len(html)} bytes")

                    # Debug snippet (first 500 chars)
                    logger.debug(f"[Playwright] HTML preview:\n{html[:500]}")

                    if 200 <= status < 300 or status == 403:
                        logger.info(f"[Playwright] Successfully loaded {final_url}")
                        return html, 200, None, final_url

                    logger.warning(f"[Playwright] Non-OK status {status} for {final_url}")
                    return html, status, f"Playwright HTTP {status}", final_url

                except PlaywrightTimeoutError:
                    logger.warning(
                        f"[Playwright] Timeout after {self.timeout_seconds}s for {url}"
                    )

                    try:
                        html = await page.content()
                        logger.debug(f"[Playwright] Timeout recovery HTML size={len(html)}")

                        if len(html) > 500:
                            logger.info("[Playwright] Recovered content after timeout")
                            return html, 200, None, url
                    except Exception as inner_e:
                        logger.debug(f"[Playwright] Failed to recover content: {inner_e}")

                    return None, 408, "Playwright timeout", url

                finally:
                    logger.debug("[Playwright] Closing browser...")
                    await browser.close()

        except Exception as e:
            logger.exception(f"[Playwright] Unexpected error: {e}")
            return None, 500, f"Playwright error: {str(e)}", url