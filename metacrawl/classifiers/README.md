# `classifiers/` — Page Type Classification Layer

Responsible for determining what **type** of page a URL represents, based on the extracted content. All classifiers implement the `BaseClassifier` interface.

## Interface

```python
class BaseClassifier(ABC):
    def classify(self, extracted_data: Dict[str, Any]) -> str:
        """
        Input:  The dictionary returned by any BaseExtractor.
        Output: A page type string.
        """
```

## Supported Page Types

| Type | Description |
|:---|:---|
| `"article"` | Long-form content — blogs, news articles, documentation |
| `"product"` | E-commerce product pages (detected via cart/buy/price keywords) |
| `"homepage"` | Sparse content with many outbound links and "home/welcome" in title |
| `"category/list"` | Index or listing pages (many links, low content density) |
| `"other"` | Default fallback when no heuristic matches |

## Files

| File | Description |
|:---|:---|
| `base.py` | `BaseClassifier` ABC |
| `heuristic_classifier.py` | `HeuristicClassifier` — rule-based classification using keyword matching, link density ratios, and content length thresholds |

## How `HeuristicClassifier` Works

The classifier evaluates the extracted data in priority order:

1. **Product** — Scores keywords like "add to cart", "buy now", "in stock", "shipping" in content and headings. ≥2 matches → product.
2. **Homepage** — Short content (<1000 chars) + many links (>20) + title contains "home"/"welcome".
3. **Category/List** — Many links (>15) + short content (<2000) + list keywords in title/headings or high link-to-content ratio.
4. **Article** — Long content (>1500 chars) or presence of "published"/"read time" in the first 1000 chars.
5. **Other** — Default fallback.

## Adding a New Classifier

```python
from metacrawl.classifiers.base import BaseClassifier

class MLClassifier(BaseClassifier):
    def classify(self, extracted_data: Dict[str, Any]) -> str:
        # ML-based classification logic
        return predicted_type
```
