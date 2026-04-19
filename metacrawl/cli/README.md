# `cli/` — Command-Line Interface

Provides the `metacrawl` CLI entrypoint using Python's `argparse`. This is the primary way to use MetaCrawl interactively.

## Files

| File | Description |
|:---|:---|
| `cli.py` | Argument parser, async runner, and output formatting |

## Entrypoints

The CLI can be invoked two ways:

```bash
# Via the installed package script (defined in pyproject.toml)
metacrawl https://example.com

# Via main.py directly
python main.py https://example.com
```

## Arguments

| Argument | Type | Required | Description |
|:---|:---|:---|:---|
| `urls` | positional | yes | One or more URLs to crawl |
| `--json` | flag | no | Output full structured results as JSON |
| `--max-topics` | int | no | Max topics to display in summary mode (default: 5) |
| `--debug` | flag | no | Enable detailed debug logging for troubleshooting |

## Output Modes

### Summary mode (default)

Prints a human-readable summary per URL:

```
Domain: en.wikipedia.org
Page Type: article
Title: Web crawler - Wikipedia
Topics: web crawler, search engine, robots txt
Content Length: 12453
Headings Found: 18
----------------------------------------
```

### JSON mode (`--json`)

Outputs the full `CrawledData` model as a JSON array:

```bash
python main.py https://example.com --json
```

## Internal Flow

1. Parses CLI arguments.
2. Calls `get_configured_pipeline()` from `utils/helpers.py` to build the pipeline.
3. Processes each URL **sequentially** via `pipeline.process_url()`.
4. Formats and prints results.
