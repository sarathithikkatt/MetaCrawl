from metacrawl.config.settings import settings
from metacrawl.pipeline.pipeline import CrawlerPipeline
from metacrawl.fetchers.http_fetcher import HttpFetcher
from metacrawl.extractors.trafilatura_extractor import TrafilaturaExtractor
from metacrawl.extractors.basic_extractor import BasicExtractor
from metacrawl.classifiers.heuristic_classifier import HeuristicClassifier
from metacrawl.topics.tfidf_extractor import TFIDFTopicExtractor

def get_configured_pipeline() -> CrawlerPipeline:
    fetcher = HttpFetcher()
    
    if settings.extractor_type == "trafilatura":
        extractor = TrafilaturaExtractor()
    else:
        extractor = BasicExtractor()
        
    classifier = HeuristicClassifier()
    
    # We always use TFIDF for now since yake is not installed by default per earlier instructions
    topic_extractor = TFIDFTopicExtractor()
    
    return CrawlerPipeline(
        fetcher=fetcher,
        extractor=extractor,
        classifier=classifier,
        topic_extractor=topic_extractor
    )
