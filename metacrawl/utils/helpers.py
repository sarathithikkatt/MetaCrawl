from metacrawl.config import settings
from metacrawl.pipeline import CrawlerPipeline
from metacrawl.fetchers import HttpFetcher, PlaywrightFetcher
from metacrawl.extractors import TrafilaturaExtractor, BasicExtractor
from metacrawl.classifiers import HeuristicClassifier
from metacrawl.topics import TFIDFTopicExtractor
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
