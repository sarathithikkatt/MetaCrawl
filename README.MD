# 🕸️ MetaCrawl

**MetaCrawl** is a robust, modular, and extensible web crawling and content extraction system. Built entirely in Python using modern async tools, it is designed to take any URL and convert its page content into a clean, structured JSON format containing text, topics, type classification, and parsed metadata.

## 🚀 Quick Start

### 1. Installation

MetaCrawl uses standard Python packaging defined in `pyproject.toml`.

To set it up locally, ideally within a virtual environment, simply run:

```bash
# Create and activate a Virtual Environment (Optional but recommended)
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# Mac/Linux: source .venv/bin/activate

# Install the package and its dependencies
pip install -e .
```

### 2. Usage

Once installed, you can use the command-line interface out of the box to test against any live URLs.

**Basic Usage:**
```bash
python -m metacrawl.cli https://en.wikipedia.org/wiki/Web_crawler
```
This will print a high-level summary of the page including Domain, Page Type, Title, and Topics extracted.

**JSON Output:**
To get the fully structured dataset (which includes the full content, heading list, and identified links/images), use the `--json` flag:
```bash
python -m metacrawl.cli https://news.ycombinator.com/ --json
```

**Multiple URLs:**
You can pass multiple URLs sequentially:
```bash
python -m metacrawl.cli https://github.blog/ https://scrapeme.live/shop/Bulbasaur/
```

## 📂 Project Structure

```text
MetaCrawl/
├── pyproject.toml              # Dependencies and package configuration
├── README.MD                   # Project overview & Setup
├── DOCUMENTATION.md            # In-depth architectural details
└── src/
    └── metacrawl/
        ├── __init__.py         # Package init
        ├── cli.py              # CLI entry point
        ├── pipeline.py         # Main orchestrator (CrawlerPipeline)
        ├── models.py           # Pydantic data schemas
        ├── interfaces.py       # Abstract Base Classes (ABCs)
        ├── fetcher.py          # HTTP networking layer (aiohttp)
        ├── extractor.py        # DOM/Content Parsing (Trafilatura & BeautifulSoup)
        ├── classifier.py       # Heuristic page type classification
        └── topics.py           # Unsupervised Topic Extraction (TF-IDF)
```

## 📚 Learn More
To learn more about the code architecture, how to write your own `Fetchers` using Playwright, or how to swap in a Machine Learning model for the `Classifier`, please read the detailed [DOCUMENTATION.md](DOCUMENTATION.md) included in this repository.
