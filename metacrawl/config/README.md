# `config/` — Centralized Settings

Manages all MetaCrawl configuration via `pydantic-settings`. Settings are auto-loaded from environment variables (prefixed with `METACRAWL_`) and an optional `.env` file.

## Files

| File | Description |
|:---|:---|
| `settings.py` | `Settings` class definition + singleton `settings` instance |

## Usage

```python
from metacrawl.config.settings import settings

print(settings.timeout)        # 15
print(settings.extractor_type) # "trafilatura"
```

All modules import the singleton `settings` object directly — no dependency injection needed for configuration.

## Full Settings Reference

| Setting | Env Variable | Type | Default | Description |
|:---|:---|:---|:---|:---|
| `timeout` | `METACRAWL_TIMEOUT` | `int` | `15` | HTTP request timeout in seconds |
| `max_retries` | `METACRAWL_MAX_RETRIES` | `int` | `3` | Max retry attempts (reserved) |
| `user_agent` | `METACRAWL_USER_AGENT` | `str` | `"MetaCrawl/2.0"` | User-Agent header |
| `use_playwright_fallback` | `METACRAWL_USE_PLAYWRIGHT_FALLBACK` | `bool` | `True` | Enable Playwright 403 fallback |
| `playwright_timeout` | `METACRAWL_PLAYWRIGHT_TIMEOUT` | `int` | `30` | Playwright page-load timeout (seconds) |
| `headless` | `METACRAWL_HEADLESS` | `bool` | `True` | Run Playwright in headless mode |
| `extractor_type` | `METACRAWL_EXTRACTOR_TYPE` | `"trafilatura" \| "basic"` | `"trafilatura"` | Which extractor implementation to use |
| `topic_model` | `METACRAWL_TOPIC_MODEL` | `"tfidf" \| "yake"` | `"tfidf"` | Which topic extractor to use |
| `log_level` | `METACRAWL_LOG_LEVEL` | `str` | `"INFO"` | Python logging level |
| `log_dir` | `METACRAWL_LOG_DIR` | `str` | `"logs"` | Directory to store log files |

## Override Examples

```bash
# Via environment variable
export METACRAWL_TIMEOUT=30
export METACRAWL_EXTRACTOR_TYPE=basic

# Via Docker
docker run -e METACRAWL_TIMEOUT=60 metacrawl "https://example.com"
```

Or create a `.env` file in the project root:

```
METACRAWL_TIMEOUT=30
METACRAWL_LOG_LEVEL=DEBUG
```
