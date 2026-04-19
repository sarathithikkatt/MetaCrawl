import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from metacrawl.api.app import app
from metacrawl.models.models import CrawledData

client = TestClient(app)

@pytest.mark.asyncio
async def test_crawl_endpoint_success():
    # Mock data to return
    mock_data = CrawledData(
        url="https://example.com",
        domain="example.com",
        title="Test Page",
        content="This is a test content",
        status_code=200,
        page_type="article"
    )
    
    # Mock the pipeline's process_url method
    # Since app.py does 'pipeline = get_configured_pipeline()', we need to mock it in app.py
    with patch("metacrawl.api.app.pipeline.process_url", new_callable=AsyncMock) as mock_process:
        mock_process.return_value = mock_data
        
        response = client.post("/crawl", json={"url": "https://example.com"})
        
    assert response.status_code == 200
    assert response.json()["title"] == "Test Page"
    assert response.json()["url"] == "https://example.com"

@pytest.mark.asyncio
async def test_crawl_endpoint_error():
    # Mock error data
    mock_error_data = CrawledData(
        url="https://example.com",
        domain="example.com",
        error="Fetch failed",
        status_code=404
    )
    
    with patch("metacrawl.api.app.pipeline.process_url", new_callable=AsyncMock) as mock_process:
        mock_process.return_value = mock_error_data
        
        response = client.post("/crawl", json={"url": "https://example.com"})
        
    assert response.status_code == 404
    assert response.json()["error"] == "Fetch failed"

def test_crawl_endpoint_invalid_url():
    response = client.post("/crawl", json={"url": "not-a-url"})
    assert response.status_code == 422 # Pydantic validation error
