from typing import Dict, Any, Type, Optional
from urllib.parse import urlparse

from metacrawl.models.models import CrawledData
from metacrawl.fetchers.base import BaseFetcher
from metacrawl.extractors.base import BaseExtractor
from metacrawl.classifiers.base import BaseClassifier
from metacrawl.topics.base import BaseTopicExtractor
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

class CrawlerPipeline:
    def __init__(self, 
                 fetcher: BaseFetcher,
                 extractor: BaseExtractor,
                 classifier: BaseClassifier,
                 topic_extractor: BaseTopicExtractor):
        self.fetcher = fetcher
        self.extractor = extractor
        self.classifier = classifier
        self.topic_extractor = topic_extractor
        
    async def process_url(self, url: str) -> CrawledData:
        domain = urlparse(url).netloc
        logger.info(f"Starting pipeline for URL: {url}")
        
        # 1. Fetch
        logger.debug(f"Fetching HTML for {url}...")
        html, status, error, final_url = await self.fetcher.fetch(url)
        
        if error or not html:
            logger.warning(f"Fetch failed for {url} with status {status}: {error}")
            return CrawledData(
                url=url,
                domain=domain,
                status_code=status,
                error=error,
                page_type="other"
            )
            
        real_domain = urlparse(final_url).netloc
        
        # 2. Extract
        logger.debug(f"Extracting content from {final_url}...")
        try:
            extracted = self.extractor.extract(html, final_url)
        except Exception as e:
            logger.error(f"Extraction error on {final_url}: {e}")
            return CrawledData(
                url=final_url,
                domain=real_domain,
                status_code=status,
                error=f"Extraction failed: {str(e)}",
                page_type="other"
            )
            
        # 3. Classify
        logger.debug(f"Classifying page {final_url}...")
        try:
            page_type = self.classifier.classify(extracted)
        except Exception as e:
            logger.error(f"Classification error on {final_url}: {e}")
            page_type = "other"
            
        # 4. Extract Topics
        topics = []
        try:
            if extracted.get("content"):
                logger.debug(f"Extracting topics for {final_url}...")
                topics = self.topic_extractor.extract_topics(extracted["content"])
        except Exception as e:
            logger.error(f"Topic extraction error on {final_url}: {e}")
            pass
            
        logger.info(f"Successfully processed {final_url} (Type: {page_type})")
        # Assemble
        return CrawledData(
            url=final_url,
            domain=real_domain,
            page_type=page_type,
            title=extracted.get("title"),
            description=extracted.get("description"),
            headings=extracted.get("headings", []),
            content=extracted.get("content", ""),
            topics=topics,
            links=extracted.get("links", []),
            images=extracted.get("images", []),
            status_code=status,
            error=None
        )
