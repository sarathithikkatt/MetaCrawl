import pytest
from unittest.mock import patch, MagicMock
from metacrawl.utils import get_configured_pipeline
from metacrawl.pipeline import CrawlerPipeline
from metacrawl.extractors import TrafilaturaExtractor, BasicExtractor

def test_get_configured_pipeline_default():
    # We should mock settings to control the outcome
    with patch("metacrawl.utils.helpers.settings") as mock_settings:
        mock_settings.extractor_type = "trafilatura"
        mock_settings.use_playwright_fallback = False
        mock_settings.topic_model = "tfidf"
        mock_settings.log_level = "DEBUG"
        
        pipeline = get_configured_pipeline()
        
    assert isinstance(pipeline, CrawlerPipeline)
    assert isinstance(pipeline.extractor, TrafilaturaExtractor)
    assert pipeline.fallback_fetcher is None

def test_get_configured_pipeline_with_fallback():
    with patch("metacrawl.utils.helpers.settings") as mock_settings:
        mock_settings.extractor_type = "basic"
        mock_settings.use_playwright_fallback = True
        mock_settings.topic_model = "tfidf"
        mock_settings.log_level = "DEBUG"
        
        pipeline = get_configured_pipeline()
        
    assert isinstance(pipeline, CrawlerPipeline)
    assert isinstance(pipeline.extractor, BasicExtractor)
    assert pipeline.fallback_fetcher is not None
