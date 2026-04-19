import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from metacrawl.cli.cli import main_async
from metacrawl.models.models import CrawledData

@pytest.mark.asyncio
async def test_cli_main_async_success():
    mock_data = CrawledData(
        url="https://example.com",
        domain="example.com",
        title="Test Page",
        content="This is a test content",
        status_code=200,
        page_type="article"
    )
    
    with patch("metacrawl.cli.cli.get_configured_pipeline") as mock_get_pipeline:
        mock_pipeline = AsyncMock()
        mock_pipeline.process_url.return_value = mock_data
        mock_get_pipeline.return_value = mock_pipeline
        
        # Test non-json output (just check if it runs without error)
        with patch("builtins.print") as mock_print:
            await main_async(["https://example.com"], json_output=False, max_topics=5)
            
            # Verify pipeline was called
            mock_pipeline.process_url.assert_called_once_with("https://example.com")
            
            # Check if domain was printed
            mock_print.assert_any_call("Domain: example.com")

@pytest.mark.asyncio
async def test_cli_main_async_json():
    mock_data = CrawledData(
        url="https://example.com",
        domain="example.com",
        title="Test Page",
        content="This is a test content",
        status_code=200,
        page_type="article"
    )
    
    with patch("metacrawl.cli.cli.get_configured_pipeline") as mock_get_pipeline:
        mock_pipeline = AsyncMock()
        mock_pipeline.process_url.return_value = mock_data
        mock_get_pipeline.return_value = mock_pipeline
        
        with patch("builtins.print") as mock_print:
            await main_async(["https://example.com"], json_output=True, max_topics=5)
            
            # Get the argument passed to print (the JSON string)
            args, _ = mock_print.call_args
            printed_json = json.loads(args[0])
            
            assert isinstance(printed_json, list)
            assert printed_json[0]["url"] == "https://example.com"
            assert printed_json[0]["title"] == "Test Page"

@pytest.mark.asyncio
async def test_cli_main_async_error():
    mock_error_data = CrawledData(
        url="https://example.com",
        domain="example.com",
        error="Fetch failed",
        status_code=404
    )
    
    with patch("metacrawl.cli.cli.get_configured_pipeline") as mock_get_pipeline:
        mock_pipeline = AsyncMock()
        mock_pipeline.process_url.return_value = mock_error_data
        mock_get_pipeline.return_value = mock_pipeline
        
        with patch("builtins.print") as mock_print:
            await main_async(["https://example.com"], json_output=False, max_topics=5)
            # Just check if it handles error without crashing
            # It prints to stderr, so we should mock sys.stderr if we want to be precise
            # But the test passing means it didn't raise an exception
