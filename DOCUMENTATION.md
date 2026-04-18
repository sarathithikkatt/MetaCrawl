# MetaCrawl Documentation & Architecture

MetaCrawl is designed around the principle of **loosely coupled, interchangeable modules**. The primary orchestrator is the `CrawlerPipeline`, which sequentially delegates tasks to four major subsystems: Network Fetching, Content Extraction, Classification, and Topic Extraction.

This architecture ensures that if you decide to scale to millions of URLs, or introduce heavy ML models, you only need to override specific components without touching the rest of the flow.

---

## 1. Core Architecture

### Interfaces First (`interfaces.py`)
To guarantee that different implementations conform to what the pipeline expects, all major components inherit from Python `Abstract Base Classes` (ABCs). This makes mocking things for unit testing incredibly easy.

- `FetcherABC` expects an asynchronous `fetch(url)` method.
- `ExtractorABC` expects an `extract(html, url)` method returning a dictionary.
- `ClassifierABC` expects a `classify(extracted_dict)` method returning a classification string.
- `TopicExtractorABC` expects an `extract_topics(text)` method returning a list of keyword topics.

### Data Contract (`models.py`)
The pipeline always yields a `CrawledData` Pydantic model. Pydantic ensures structure enforcement and handles serialization automatically. 
If an error happens during network fetch, the `error` field is populated while everything else degrades gracefully.

---

## 2. Component Deep Dive

### Network Fetcher (`fetcher.py`)
Currently implemented via **`AsyncFetcher`** using `aiohttp`.
- It executes a non-blocking request with configurable timeouts and User-Agent headers.
- Crucially, it manages redirects and passes both the `final_url` and HTTP `status` code smoothly down the chain.

*(Future scale idea: Swap out `AsyncFetcher` with a `PlaywrightFetcher` if you must process heavy single-page JS applications).*

### Content Extractor (`extractor.py`)
Implemented via **`HTMLExtractor`** wrapping `BeautifulSoup4` and `trafilatura`.
- Retrieves simple metadata like Title and Description using standard `meta` tags.
- Identifies headers (`<h1>`, `<h2>`, `<h3>`).
- Uses `trafilatura`, a state-of-the-art heuristic text block parser, to reliably slice away navigation and footer noise and return **just the main body content**.
- Collects absolute URLs (`links`) and images.

### Heuristic Classifier (`classifier.py`)
Implemented via **`HeuristicClassifier`**.
We bypass costly Machine Learning models here and instead rely on rule sets, regex, and feature thresholds:
- Checks links-to-content ratios (High ratio = `category/list` or `homepage`)
- Looks for targeted keywords (e.g., "Add to Cart", "Price", "SKU") to tag `product` pages.
- Looks for authorship syntax or high absolute content length for `article`.

### Topic Extractor (`topics.py`)
Implemented via **`TFIDFTopicExtractor`**.
Extracts crucial contextual themes out of the main site content using `scikit-learn`'s `TfidfVectorizer`.
- Identifies n-grams (single words or two-word chunks).
- Filters out universal English Stop Words.
- Scores frequency and assigns a normalized weight, pulling only the top 5 default themes.

---

## 3. Extending the System

If you want to create a new way to fetch pages, for instance using headless Chrome:

1. Create a new class: `class HeadlessFetcher(FetcherABC):`
2. Implement your asynchronous `fetch()` method using Pyppeteer or Playwright.
3. Inject it into the pipeline orchestrator:

```python
from metacrawl.pipeline import CrawlerPipeline
from my_custom_modules import HeadlessFetcher, TransformerClassifier

# Dependency Injection!
custom_pipeline = CrawlerPipeline(
    fetcher=HeadlessFetcher(),
    classifier=TransformerClassifier() 
)

data = await custom_pipeline.process_url("https://example.com/js-heavy-app")
```
