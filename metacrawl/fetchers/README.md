# `fetchers/` — Network Fetching Layer

Responsible for downloading raw HTML content from a given URL. All fetchers implement the `BaseFetcher` abstract interface, ensuring they are interchangeable within the pipeline.

## Interface

```python
class BaseFetcher(ABC):
    async def fetch(self, url: str) -> Tuple[Optional[str], int, Optional[str], str]:
        """
        Returns: (raw_html, status_code, error_message, final_url)
        - raw_html: The page HTML string, or None on failure.
        - status_code: HTTP status code (e.g. 200, 403, 408, 500).
        - error_message: None on success, descriptive string on failure.
        - final_url: The URL after any redirects.
        """
```

## Files

| File | Description |
|:---|:---|
| `base.py` | `BaseFetcher` ABC — the contract all fetchers must satisfy |
| `http_fetcher.py` | `HttpFetcher` — primary fetcher using `aiohttp` with configurable timeout and user-agent |
| `playwright_fetcher.py` | `PlaywrightFetcher` — headless Chromium fallback with `playwright-stealth` integration for bot-protected sites |

## How Fallback Works

The pipeline does **not** handle fallback logic inside the fetcher. Instead, `CrawlerPipeline` accepts an optional `fallback_fetcher` parameter. When the primary `HttpFetcher` returns a **403 Forbidden**, the pipeline automatically retries with the fallback (typically `PlaywrightFetcher`). This is toggled via `settings.use_playwright_fallback`.

## Configuration

| Setting | Default | Description |
|:---|:---|:---|
| `METACRAWL_TIMEOUT` | `15` | `HttpFetcher` request timeout (seconds) |
| `METACRAWL_USER_AGENT` | `MetaCrawl/2.0` | User-Agent header string |
| `METACRAWL_USE_PLAYWRIGHT_FALLBACK` | `True` | Enable/disable Playwright 403 fallback |
| `METACRAWL_PLAYWRIGHT_TIMEOUT` | `30` | Playwright page load timeout (seconds) |
| `METACRAWL_HEADLESS` | `True` | Run Playwright in headless mode |

## Adding a New Fetcher

```python
from metacrawl.fetchers.base import BaseFetcher

class SeleniumFetcher(BaseFetcher):
    async def fetch(self, url: str):
        # Your implementation here
        return html, status_code, error, final_url
```

Then register it in `utils/helpers.py` or inject it directly into `CrawlerPipeline`.
