import pytest
import aiohttp
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from metacrawl.fetchers.http_fetcher import HttpFetcher
from metacrawl.fetchers.playwright_fetcher import PlaywrightFetcher

@pytest.mark.asyncio
async def test_http_fetcher_success():
    fetcher = HttpFetcher()
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.url = "https://example.com/final"
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.text.return_value = "<html>Success</html>"
    
    # Correct mocking for async context manager session.get(...) as response
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    # aiohttp.ClientSession(timeout=timeout, headers=headers) as session
    mock_session_cm = MagicMock()
    mock_session_cm.__aenter__.return_value = mock_session
    
    with patch("aiohttp.ClientSession", return_value=mock_session_cm):
        html, status, error, final_url = await fetcher.fetch("https://example.com")
        
    assert html == "<html>Success</html>"
    assert status == 200
    assert error is None
    assert final_url == "https://example.com/final"

@pytest.mark.asyncio
async def test_http_fetcher_unsupported_content_type():
    fetcher = HttpFetcher()
    
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.url = "https://example.com/image.png"
    mock_response.headers = {"Content-Type": "image/png"}
    
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    mock_session_cm = MagicMock()
    mock_session_cm.__aenter__.return_value = mock_session
    
    with patch("aiohttp.ClientSession", return_value=mock_session_cm):
        html, status, error, final_url = await fetcher.fetch("https://example.com/image.png")
        
    assert html is None
    assert status == 415
    assert "Unsupported Content-Type" in error

@pytest.mark.asyncio
async def test_http_fetcher_timeout():
    fetcher = HttpFetcher(timeout_seconds=1)
    
    mock_session_cm = MagicMock()
    mock_session_cm.__aenter__.side_effect = asyncio.TimeoutError()
    
    with patch("aiohttp.ClientSession", return_value=mock_session_cm):
        html, status, error, final_url = await fetcher.fetch("https://example.com")
        
    assert html is None
    assert status == 408
    assert "Request timed out" in error

@pytest.mark.asyncio
async def test_playwright_fetcher_success():
    fetcher = PlaywrightFetcher(timeout_seconds=5, headless=True)
    
    # Very deep mocking for Playwright
    mock_page = AsyncMock()
    mock_page.goto.return_value = AsyncMock(status=200, headers={"content-type": "text/html"})
    mock_page.content.return_value = "<html>Playwright Success</html>"
    mock_page.url = "https://example.com/playwright"
    
    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page
    
    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    
    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser
    
    with patch("metacrawl.fetchers.playwright_fetcher.async_playwright") as mock_ap:
        mock_ap.return_value.__aenter__.return_value = mock_playwright
        
        # We also need to mock Stealth
        with patch("metacrawl.fetchers.playwright_fetcher.Stealth") as mock_stealth:
            mock_stealth.return_value.apply_stealth_async = AsyncMock()
            
            html, status, error, final_url = await fetcher.fetch("https://example.com")
            
    assert html == "<html>Playwright Success</html>"
    assert status == 200
    assert error is None
    assert final_url == "https://example.com/playwright"
