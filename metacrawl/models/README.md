# `models/` — Shared Data Schemas

Defines the Pydantic models that serve as the **data contract** between all pipeline components. Using validated models instead of raw dicts ensures type safety and serialization consistency.

## Files

| File | Description |
|:---|:---|
| `models.py` | `CrawledData` and `ImageMeta` Pydantic models |

## Schemas

### `CrawledData`

The primary output model returned by `CrawlerPipeline.process_url()`.

| Field | Type | Default | Description |
|:---|:---|:---|:---|
| `url` | `str` | — | Final URL after redirects |
| `domain` | `str` | — | Extracted domain (e.g. `en.wikipedia.org`) |
| `page_type` | `str` | `"other"` | Classifier result: `article`, `product`, `homepage`, `category/list`, `other` |
| `title` | `str \| None` | `None` | Page `<title>` tag content |
| `description` | `str \| None` | `None` | Meta description or OG description |
| `headings` | `List[str]` | `[]` | h1/h2/h3 heading text |
| `content` | `str` | `""` | Main body text |
| `topics` | `List[str]` | `[]` | Extracted topic keywords |
| `links` | `List[str]` | `[]` | Absolute URLs found on the page |
| `images` | `List[ImageMeta]` | `[]` | Image sources and alt text |
| `status_code` | `int` | `200` | HTTP status code of the fetch |
| `error` | `str \| None` | `None` | Error message if the fetch/extraction failed |

### `ImageMeta`

| Field | Type | Default | Description |
|:---|:---|:---|:---|
| `src` | `str` | — | Absolute image URL |
| `alt` | `str \| None` | `None` | Alt text of the image |

## Serialization

All models support `.model_dump()` and `.model_dump_json()` for JSON export:

```python
data = await pipeline.process_url("https://example.com")
print(data.model_dump_json(indent=2))
```
