# `utils/` — Shared Utilities

Contains factory functions, dependency injection wiring, and the centralized logging setup. This is the **composition root** of MetaCrawl — where abstract interfaces are bound to concrete implementations.

## Files

| File | Description |
|:---|:---|
| `helpers.py` | `get_configured_pipeline()` — the factory function that builds a fully-wired `CrawlerPipeline` based on settings |
| `logger.py` | `get_logger(name)` — returns a configured Python `logging.Logger` with standardized format and settings-driven log level |

## `get_configured_pipeline()`

This is the single function that constructs the default pipeline. It reads from `settings` to decide:

- **Fetcher**: Always `HttpFetcher`, with `PlaywrightFetcher` as optional fallback (if `settings.use_playwright_fallback` is `True`).
- **Extractor**: `TrafilaturaExtractor` or `BasicExtractor` based on `settings.extractor_type`.
- **Classifier**: Always `HeuristicClassifier`.
- **Topic Extractor**: Always `TFIDFTopicExtractor`.

```python
from metacrawl.utils.helpers import get_configured_pipeline

pipeline = get_configured_pipeline()
result = await pipeline.process_url("https://example.com")
```

Both the CLI and the API use this function to get their pipeline instance.

## `get_logger(name)`

Creates a logger with:
- **Level**: Driven by `settings.log_level` (default: `INFO`).
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Output**: `stdout`
- **Deduplication**: Only adds handlers once per logger name to prevent duplicate log lines.

```python
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Ready")
```
