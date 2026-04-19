# 🕸️ MetaCrawl

**MetaCrawl** is a robust, modular, and extensible web crawling and content extraction system. Built entirely in Python using modern async tools, it is designed to take any URL and convert its page content into a clean, structured JSON format containing text, topics, type classification, and parsed metadata.

## ✨ Key Features

- **🚀 Async Architecture**: Built on `asyncio` and `aiohttp` for high-performance concurrent crawling.
- **🛡️ Stealth Fetching**: Integrates `playwright-stealth` to bypass basic bot detection and scraping protections.
- **🧩 Modular Extractors**: Support for both `trafilatura` (advanced content extraction) and a `basic` BeautifulSoup-based fallback.
- **🏷️ Smart Classification**: Automatic page type detection (Article, Product, Homepage, etc.) using heuristic analysis.
- **🧠 Topic Extraction**: NLP-driven topic identification via TF-IDF and scikit-learn.
- **🌐 FastAPI Ready**: Includes a production-ready HTTP API for remote crawling tasks.

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

# Install Chromium binaries for Playwright fallback
playwright install chromium
```

### 2. Usage

Once installed, you can use the command-line interface out of the box to test against any live URLs.

**Basic CLI Usage:**
```bash
python main.py https://en.wikipedia.org/wiki/Web_crawler
```
This will print a high-level summary of the page including Domain, Page Type, Title, and Topics extracted.

**JSON Output:**
To get the fully structured dataset (which includes the full content, description, heading list, and identified links/images), use the `--json` flag:
```bash
python main.py https://news.ycombinator.com/ --json
```

**Debug Mode:**
Enable detailed logging for troubleshooting:
```bash
python main.py https://example.com --debug
```

---

## 🐳 Docker Execution

You can run MetaCrawl entirely via Docker without installing Python locally.

```bash
# Build the image
docker build -t metacrawl .

# Run the CLI inside Docker
docker run metacrawl "https://github.blog"
```

## 🌐 API Mode (FastAPI)

MetaCrawl includes a built-in FastAPI application for API usage. Spin it up using Docker Compose:

```bash
docker compose up --build
```
This serves the application on `http://localhost:8000`. 
You can test the endpoint:
```bash
curl -X POST "http://localhost:8000/crawl" -H "Content-Type: application/json" -d '{"url":"https://example.com"}'
```

---

## ⚙️ Configuration

MetaCrawl is managed using `pydantic-settings`. Configs are read from environment variables matching the `METACRAWL_` prefix.

| Env Variable | Default | Description |
| :--- | :--- | :--- |
| `METACRAWL_TIMEOUT` | `15` | Networking max timeout (seconds) |
| `METACRAWL_EXTRACTOR_TYPE` | `trafilatura` | Either `trafilatura` (advanced) or `basic` (fallback parsing) |
| `METACRAWL_LOG_LEVEL` | `INFO` | Application logging (`INFO`, `DEBUG`, `WARNING`) |
| `METACRAWL_HEADLESS` | `True` | Run Playwright in headless mode |
| `METACRAWL_USE_PLAYWRIGHT_FALLBACK` | `True` | Enable Playwright if HTTP fetch fails or returns 403 |
| `METACRAWL_USER_AGENT` | (Standard) | Custom User-Agent string |


## 📂 Project Structure

```text
MetaCrawl/
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Fast API spin-up config
├── pyproject.toml              # Dependencies config
├── main.py                     # Root CLI entry target
├── README.MD                   # Project overview & Setup
├── DOCUMENTATION.md            # Architectural detail
└── metacrawl/
    ├── api/                    # FastAPI routes
    ├── cli/                    # Argparse CLI builder
    ├── classifiers/            # Heuristic and structural detectors via BaseClassifier
    ├── config/                 # Pydantic Settings base
    ├── extractors/             # HTML data extraction via BaseExtractor
    ├── fetchers/               # HTTP clients via BaseFetcher
    ├── models/                 # Shared Data Schemas
    ├── pipeline/               # Injection logic orchestration
    ├── topics/                 # TF-IDF Topic detection via BaseTopicExtractor
    └── utils/                  # Factory bindings and DI logic
```

## 📚 Learn More
To learn more about the code architecture, how to plug in alternative Fetchers or Classifiers, read the detailed [DOCUMENTATION.md](DOCUMENTATION.md).
