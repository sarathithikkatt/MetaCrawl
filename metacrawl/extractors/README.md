# `extractors/` — Content Extraction Layer

Responsible for parsing raw HTML into structured data: title, meta description, headings, main body content, links, and images. All extractors implement the `BaseExtractor` interface.

## Interface

```python
class BaseExtractor(ABC):
    def extract(self, html: str, url: str) -> Dict[str, Any]:
        """
        Returns a dictionary with these keys:
        - title: str | None
        - description: str | None
        - headings: List[str]       — h1/h2/h3 text
        - content: str              — main body text
        - links: List[str]          — absolute URLs found on the page
        - images: List[{src, alt}]  — image metadata
        """
```

> **Note**: This is a **synchronous** method. Extraction operates on already-fetched HTML, so no I/O is needed.

## Files

| File | Description |
|:---|:---|
| `base.py` | `BaseExtractor` ABC — defines the extraction contract |
| `trafilatura_extractor.py` | `TrafilaturaExtractor` — uses the `trafilatura` library for advanced boilerplate removal and main-content isolation. Falls back to raw `bs4` text if trafilatura fails. |
| `basic_extractor.py` | `BasicExtractor` — simple BeautifulSoup-only extractor that dumps all page text. Useful as a fallback or for pages where trafilatura struggles. |

## Which Extractor Is Used?

Controlled by `settings.extractor_type`:

| Value | Extractor | When to use |
|:---|:---|:---|
| `"trafilatura"` (default) | `TrafilaturaExtractor` | Best for articles, blogs, news — strips nav/footer/ads |
| `"basic"` | `BasicExtractor` | When you need all page text including boilerplate |

Set via environment: `METACRAWL_EXTRACTOR_TYPE=basic`

## Adding a New Extractor

```python
from metacrawl.extractors.base import BaseExtractor

class ReadabilityExtractor(BaseExtractor):
    def extract(self, html: str, url: str) -> Dict[str, Any]:
        # Your implementation
        return {"title": ..., "description": ..., "headings": ..., "content": ..., "links": ..., "images": ...}
```

Register in `utils/helpers.py` under the `extractor_type` switch.
