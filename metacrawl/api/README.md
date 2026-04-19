# `api/` — FastAPI HTTP Interface

Exposes MetaCrawl as an HTTP API using FastAPI, enabling remote crawl requests over the network.

## Files

| File | Description |
|:---|:---|
| `app.py` | FastAPI application, route definitions, request/response models |

## Endpoints

### `POST /crawl`

Crawl a single URL and return structured data.

**Request body:**

```json
{
  "url": "https://example.com"
}
```

**Response:** A full `CrawledData` JSON object (see `models/README.md` for schema).

**Error responses:**

| Status | Condition |
|:---|:---|
| `400` | Bad request (e.g., invalid URL format) |
| `404` | Resource not found or page missing |
| `403` | Fetch returned 403 and fallback also failed |
| `500` | Unexpected server error during processing |

## Running the API

### Locally

```bash
python -m metacrawl.api.app
# Serves on http://localhost:8000 with auto-reload
```

### Via Docker Compose

```bash
docker compose up --build
# Serves on http://localhost:8000
```

### Testing

```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Interactive Docs

FastAPI auto-generates interactive API docs at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
