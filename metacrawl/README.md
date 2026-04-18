# `metacrawl/` — Core Package

This is the root package for MetaCrawl. All crawling logic is organized into domain-specific submodules following a **dependency inversion** architecture — every major component implements an abstract base class (`ABC`), and the pipeline orchestrates them without knowing their concrete implementations.

## Module Map

| Module | Purpose | Key Abstraction |
|:---|:---|:---|
| [`fetchers/`](fetchers/) | Downloads raw HTML from URLs | `BaseFetcher` |
| [`extractors/`](extractors/) | Parses HTML into structured data (title, content, links, images) | `BaseExtractor` |
| [`classifiers/`](classifiers/) | Determines page type (article, product, homepage, etc.) | `BaseClassifier` |
| [`topics/`](topics/) | Extracts key topics from page text via NLP | `BaseTopicExtractor` |
| [`pipeline/`](pipeline/) | Orchestrates fetch → extract → classify → topics | `CrawlerPipeline` |
| [`models/`](models/) | Pydantic data schemas shared across all modules | `CrawledData` |
| [`config/`](config/) | Centralized settings via `pydantic-settings` | `Settings` |
| [`cli/`](cli/) | Command-line interface (argparse) | `main()` |
| [`api/`](api/) | HTTP API interface (FastAPI) | `POST /crawl` |
| [`utils/`](utils/) | Factory functions, logging, and shared helpers | `get_configured_pipeline()` |

## Data Flow

```
URL
 │
 ▼
BaseFetcher.fetch(url) ──► (html, status, error, final_url)
 │
 ▼
BaseExtractor.extract(html, url) ──► {title, description, headings, content, links, images}
 │
 ▼
BaseClassifier.classify(extracted) ──► "article" | "product" | "homepage" | "category/list" | "other"
 │
 ▼
BaseTopicExtractor.extract_topics(content) ──► ["topic1", "topic2", ...]
 │
 ▼
CrawledData (Pydantic model — the unified output)
```

## Extending the System

1. **Create a new implementation** by subclassing the relevant `base.py` ABC.
2. **Register it** in `utils/helpers.py` → `get_configured_pipeline()`, or inject it directly when constructing `CrawlerPipeline`.
3. No other module needs to change — the pipeline is fully decoupled.

## Configuration

All modules read from `config/settings.py` which auto-loads environment variables prefixed with `METACRAWL_`. See [config/README.md](config/README.md) for the full settings reference.
