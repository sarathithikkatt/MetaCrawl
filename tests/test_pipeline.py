import pytest
from unittest.mock import AsyncMock, MagicMock
from metacrawl.pipeline import CrawlerPipeline
from metacrawl.models import CrawledData

@pytest.mark.asyncio
async def test_pipeline_handles_challenge_with_fallback():
    # Mock components
    fetcher = AsyncMock()
    extractor = MagicMock()
    classifier = MagicMock()
    topic_extractor = MagicMock()
    fallback_fetcher = AsyncMock()
    
    pipeline = CrawlerPipeline(
        fetcher=fetcher,
        extractor=extractor,
        classifier=classifier,
        topic_extractor=topic_extractor,
        fallback_fetcher=fallback_fetcher
    )
    
    # Mock robots.txt check to always allow
    pipeline._is_allowed_by_robots = AsyncMock(return_value=True)
    
    # 1. First fetch returns a challenge page
    fetcher.fetch.return_value = ("<html>Challenge</html>", 200, None, "https://amazon.com/product")
    extractor.extract.side_effect = [
        {"content": "continue shopping", "title": "Amazon.com"}, # First extraction
        {"content": "Real Product Content", "title": "Toaster"}   # Second extraction (after fallback)
    ]
    classifier.classify.side_effect = [
        "challenge", # First classification
        "product"    # Second classification
    ]
    topic_extractor.extract_topics.return_value = ["home"]
    
    # 2. Fallback fetch returns real content
    fallback_fetcher.fetch.return_value = ("<html>Real Content</html>", 200, None, "https://amazon.com/product")
    
    result = await pipeline.process_url("https://amazon.com/product")
    
    # Verify fallback was called
    fallback_fetcher.fetch.assert_called_once_with("https://amazon.com/product")
    
    # Verify final result is the product
    assert result.page_type == "product"
    assert result.content == "Real Product Content"
    assert result.status_code == 200

@pytest.mark.asyncio
async def test_pipeline_no_fallback_on_challenge():
    # Mock components without fallback
    fetcher = AsyncMock()
    extractor = MagicMock()
    classifier = MagicMock()
    topic_extractor = MagicMock()
    
    pipeline = CrawlerPipeline(
        fetcher=fetcher,
        extractor=extractor,
        classifier=classifier,
        topic_extractor=topic_extractor,
        fallback_fetcher=None
    )
    
    pipeline._is_allowed_by_robots = AsyncMock(return_value=True)
    
    fetcher.fetch.return_value = ("<html>Challenge</html>", 200, None, "https://amazon.com/product")
    extractor.extract.return_value = {"content": "continue shopping", "title": "Amazon.com"}
    classifier.classify.return_value = "challenge"
    topic_extractor.extract_topics.return_value = []
    
    result = await pipeline.process_url("https://amazon.com/product")
    
    # Result should still be challenge because no fallback was provided
    assert result.page_type == "challenge"
    assert "continue shopping" in result.content
