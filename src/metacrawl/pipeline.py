import asyncio
from typing import Dict, Any, Type
from .models import CrawledData
from .fetcher import AsyncFetcher
from .extractor import HTMLExtractor
from .classifier import HeuristicClassifier
from .topics import TFIDFTopicExtractor
from urllib.parse import urlparse

class CrawlerPipeline:
    def __init__(self, 
                 fetcher=None,
                 extractor=None,
                 classifier=None,
                 topic_extractor=None):
        self.fetcher = fetcher or AsyncFetcher()
        self.extractor = extractor or HTMLExtractor()
        self.classifier = classifier or HeuristicClassifier()
        self.topic_extractor = topic_extractor or TFIDFTopicExtractor()
        
    async def process_url(self, url: str) -> CrawledData:
        domain = urlparse(url).netloc
        
        # 1. Fetch
        html, status, error, final_url = await self.fetcher.fetch(url)
        
        if error or not html:
            return CrawledData(
                url=url,
                domain=domain,
                status_code=status,
                error=error,
                page_type="other"
            )
            
        real_domain = urlparse(final_url).netloc
        
        # 2. Extract
        try:
            extracted = self.extractor.extract(html, final_url)
        except Exception as e:
            return CrawledData(
                url=final_url,
                domain=real_domain,
                status_code=status,
                error=f"Extraction failed: {str(e)}",
                page_type="other"
            )
            
        # 3. Classify
        try:
            page_type = self.classifier.classify(extracted)
        except Exception as e:
            page_type = "other"
            
        # 4. Extract Topics
        topics = []
        try:
            if extracted.get("content"):
                topics = self.topic_extractor.extract_topics(extracted["content"])
        except Exception as e:
            pass
            
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
