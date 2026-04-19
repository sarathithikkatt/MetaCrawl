# MetaCrawl Documentation & Architecture

MetaCrawl's massive refactor implements strict dependency inversion principles and clean module boundaries for maximum scalability.

---

## 1. Core Architecture

### Decoupled Sub-Directories
To guarantee implementation independence, each piece of the crawl logic resides in its own root configuration separated by responsibilities:
- `metacrawl/fetchers/`
- `metacrawl/extractors/`
- `metacrawl/classifiers/`
- `metacrawl/topics/`

Inside each sub-directory, a unified `base.py` guarantees the typing boundaries through standard Python `abc.ABC` definitions.

### Data Contract (`metacrawl/models/models.py`)
The pipeline securely passes a validated `CrawledData` Pydantic model everywhere instead of fragile dicts.

### Pipeline Injection (`metacrawl/pipeline/pipeline.py`)
The `CrawlerPipeline` itself takes completely built instances of `BaseFetcher`, `BaseExtractor`, etc. It has absolutely zero concept of *how* these act, it only strings their responses together and monitors fail states gracefully. It also handles advanced **Challenge/Bot Detection** logic by automatically retrying pages classified as challenges using the configured fallback fetcher.

---

## 2. Component Deep Dive

### Network Fetchers
Implemented abstractly over `BaseFetcher`. The main implementation is `HttpFetcher` (powered by `aiohttp`), securely loading connection `timeouts` and custom `user_agents` implicitly mapped via the environment configuration.

Additionally, a `PlaywrightFetcher` is included which acts as an automatic fallback mechanism when `HttpFetcher` encounters a `403 Forbidden` response, enabling robust extraction for JS-heavy or protected sites. This behavior can be toggled via `settings.use_playwright_fallback`.

### Content Extractors
`BaseExtractor` allows stringing complex parsers. Included implementations:
- `TrafilaturaExtractor`: Strips aggressive boilerplate off a target site relying cleanly upon DOM clustering logic.
- `BasicExtractor`: The fallback safety implementation dropping everything from standard `bs4` nodes directly into the string.

### Heuristic Classifier
Categorizes inputs utilizing link density, regex heuristics, and keyword triggers (`category/list`, `product`, `article`, `challenge`). The `challenge` type specifically detects bot-detection screens like Amazon's "continue shopping" or Captchas. Fully encapsulated in `classifiers/`.

### Topic Extractor
Uses `Scikit-Learn`'s `TfidfVectorizer` loaded via `topics/tfidf_extractor.py` ensuring localized NLP logic doesn't bleed into core parsers.

---

## 3. Extending the System

To harness the Dependency Injection architecture cleanly to create Custom Modules:

1. Subclass an existing API Base Class from a module folder:
```python
from metacrawl.fetchers.base import BaseFetcher

class PuppeteerFetcher(BaseFetcher):
    async def fetch(self, url: str):
        # your unique JS headless execution here
        return html, status, None, final_url
```

2. Register the dependency when instantiating the unified Orchestrator:
```python
from metacrawl.pipeline.pipeline import CrawlerPipeline
from metacrawl.extractors.trafilatura_extractor import TrafilaturaExtractor

custom_pipe = CrawlerPipeline(
    fetcher=PuppeteerFetcher(),   # <--- injected newly
    extractor=TrafilaturaExtractor(),
    classifier=...,
    topic_extractor=...
)

await custom_pipe.process_url("https://example.com")
```

---

## 4. Configuration Layer

`metacrawl/config/settings.py` utilizes the ultra-modern `pydantic-settings` to robustly intercept arbitrary environment strings directly mapped via the `METACRAWL_` namespace prefix, handling type casting automatically.

You never have to pass `timeout=15` explicitly to a class constructor, because the classes read `settings.timeout` which gets overwritten implicitly via systems like `docker run -e METACRAWL_TIMEOUT=300 metacrawl ...`.
