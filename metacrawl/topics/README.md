# `topics/` — Topic Extraction Layer

Responsible for extracting key topics/keywords from the main body text of a page using NLP techniques. All topic extractors implement the `BaseTopicExtractor` interface.

## Interface

```python
class BaseTopicExtractor(ABC):
    def extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """
        Input:  Cleaned main body text (from the extractor's "content" field).
        Output: List of topic strings, ordered by relevance.
        """
```

## Files

| File | Description |
|:---|:---|
| `base.py` | `BaseTopicExtractor` ABC |
| `tfidf_extractor.py` | `TFIDFTopicExtractor` — uses scikit-learn's `TfidfVectorizer` to identify the most important unigrams and bigrams |

## How `TFIDFTopicExtractor` Works

1. Returns empty list if the text has fewer than 10 words (not enough signal).
2. Builds a single-document TF-IDF matrix with English stop words removed.
3. Considers both unigrams and bigrams (`ngram_range=(1, 2)`).
4. Generates `max_topics × 3` candidate features, then returns the top `max_topics` by TF-IDF score.

## Configuration

| Setting | Default | Description |
|:---|:---|:---|
| `METACRAWL_TOPIC_MODEL` | `"tfidf"` | Which topic extractor to use. Currently only `"tfidf"` is functional. `"yake"` is a defined option but not implemented. |

## Adding a New Topic Extractor

```python
from metacrawl.topics.base import BaseTopicExtractor

class YAKETopicExtractor(BaseTopicExtractor):
    def extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        # YAKE-based extraction
        return topics
```

Register in `utils/helpers.py` under the `topic_model` switch.
