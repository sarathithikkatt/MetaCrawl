from metacrawl.config.settings import settings
from metacrawl.pipeline.pipeline import CrawlerPipeline
from metacrawl.fetchers.http_fetcher import HttpFetcher
from metacrawl.fetchers.playwright_fetcher import PlaywrightFetcher
from metacrawl.extractors.trafilatura_extractor import TrafilaturaExtractor
from metacrawl.extractors.basic_extractor import BasicExtractor
from metacrawl.classifiers.heuristic_classifier import HeuristicClassifier
from metacrawl.topics.tfidf_extractor import TFIDFTopicExtractor
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

def get_configured_pipeline() -> CrawlerPipeline:
    logger.info("Building pipeline with current settings")
    logger.debug(
        f"Pipeline config: extractor={settings.extractor_type}, "
        f"playwright_fallback={settings.use_playwright_fallback}, "
        f"topic_model={settings.topic_model}, log_level={settings.log_level}"
    )

    fetcher = HttpFetcher()
    fallback_fetcher = None
    if settings.use_playwright_fallback:
        fallback_fetcher = PlaywrightFetcher()
        logger.debug("Playwright fallback fetcher enabled")
    else:
        logger.debug("Playwright fallback fetcher disabled")
    
    if settings.extractor_type == "trafilatura":
        extractor = TrafilaturaExtractor()
    else:
        extractor = BasicExtractor()
    logger.debug(f"Using extractor: {extractor.__class__.__name__}")
        
    classifier = HeuristicClassifier()
    
    # We always use TFIDF for now since yake is not installed by default per earlier instructions
    topic_extractor = TFIDFTopicExtractor()
    
    logger.info("Pipeline ready")
    return CrawlerPipeline(
        fetcher=fetcher,
        extractor=extractor,
        classifier=classifier,
        topic_extractor=topic_extractor,
        fallback_fetcher=fallback_fetcher
    )
