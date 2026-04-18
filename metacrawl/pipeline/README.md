# `pipeline/` — Orchestration Layer

The core of MetaCrawl. `CrawlerPipeline` wires together all the domain components (fetcher, extractor, classifier, topic extractor) and runs them in sequence to produce a fully structured `CrawledData` output.

## Files

| File | Description |
|:---|:---|
| `pipeline.py` | `CrawlerPipeline` — the single orchestrator class |

## `CrawlerPipeline` API

```python
class CrawlerPipeline:
    def __init__(self,
                 fetcher: BaseFetcher,
                 extractor: BaseExtractor,
                 classifier: BaseClassifier,
                 topic_extractor: BaseTopicExtractor,
                 fallback_fetcher: Optional[BaseFetcher] = None):
        ...

    async def process_url(self, url: str) -> CrawledData:
        """Run the full pipeline on a single URL and return structured data."""
```

## Execution Steps

`process_url(url)` executes these stages in order:

1. **Fetch** — calls `self.fetcher.fetch(url)` to download HTML.
2. **Fallback** — if status is `403` and `fallback_fetcher` is set, retries with that fetcher.
3. **Extract** — calls `self.extractor.extract(html, final_url)` to parse structured data.
4. **Classify** — calls `self.classifier.classify(extracted_data)` to determine page type.
5. **Topics** — calls `self.topic_extractor.extract_topics(content)` to find key topics.
6. **Assemble** — builds and returns a `CrawledData` Pydantic model.

Each stage is wrapped in error handling — if extraction, classification, or topic extraction fails, the pipeline returns a partial result rather than crashing.

## Design Principle

The pipeline has **zero knowledge** of concrete implementations. It operates purely on abstract interfaces. This means you can swap any component without touching pipeline code — just inject different instances at construction time.

## Usage

```python
from metacrawl.utils.helpers import get_configured_pipeline

pipeline = get_configured_pipeline()
result = await pipeline.process_url("https://example.com")
print(result.model_dump_json(indent=2))
```
