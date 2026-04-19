from typing import Dict, Any, Type, Optional
from urllib.parse import urlparse, urljoin
import urllib.robotparser
import asyncio
import time

from metacrawl.models.models import CrawledData
from metacrawl.fetchers.base import BaseFetcher
from metacrawl.extractors.base import BaseExtractor
from metacrawl.classifiers.base import BaseClassifier
from metacrawl.topics.base import BaseTopicExtractor
from metacrawl.config.settings import settings
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

class CrawlerPipeline:
    def __init__(self, 
                 fetcher: BaseFetcher,
                 extractor: BaseExtractor,
                 classifier: BaseClassifier,
                 topic_extractor: BaseTopicExtractor,
                 fallback_fetcher: Optional[BaseFetcher] = None):
        self.fetcher = fetcher
        self.extractor = extractor
        self.classifier = classifier
        self.topic_extractor = topic_extractor
        self.fallback_fetcher = fallback_fetcher
        self._robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last_request_time: Dict[str, float] = {}
        
    async def _is_allowed_by_robots(self, url: str) -> bool:
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = urljoin(domain, "/robots.txt")
        
        if domain not in self._robots_cache:
            logger.debug(f"Fetching robots.txt from {robots_url}")
            rp = urllib.robotparser.RobotFileParser()
            try:
                # We use a simple fetch since robotparser.read() is blocking
                # For a more robust async implementation, we could fetch manually
                # but for "basic mention", this is a good start.
                rp.set_url(robots_url)
                # robotparser.read() is blocking, but in a small tool like this 
                # we can wrap it or just use it.
                await asyncio.to_thread(rp.read)
                self._robots_cache[domain] = rp
            except Exception as e:
                logger.warning(f"Could not fetch/parse robots.txt for {domain}: {e}")
                return True # Assume allowed if robots.txt fails
                
        rp = self._robots_cache[domain]
        return rp.can_fetch(self.fetcher.user_agent if hasattr(self.fetcher, 'user_agent') else "*", url)

    async def process_url(self, url: str) -> CrawledData:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        base_domain = f"{parsed_url.scheme}://{domain}"
        logger.info(f"Starting pipeline for URL: {url}")
        
        # 0. Rate limiting
        last_time = self._last_request_time.get(base_domain, 0)
        elapsed = time.time() - last_time
        if elapsed < settings.rate_limit_delay:
            wait_time = settings.rate_limit_delay - elapsed
            logger.debug(f"Rate limiting {domain}: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        
        # 1. Robots.txt check
        if not await self._is_allowed_by_robots(url):
            logger.warning(f"URL disallowed by robots.txt: {url}")
            return CrawledData(
                url=url,
                domain=domain,
                status_code=403,
                error="Disallowed by robots.txt",
                page_type="other"
            )

        # 2. Fetch
        logger.debug(f"Fetching HTML for {url}...")
        self._last_request_time[base_domain] = time.time()
        html, status, error, final_url = await self.fetcher.fetch(url)
        
        # Check for 403 and fallback fetcher configured
        if status == 403 and self.fallback_fetcher:
            logger.warning(f"Fetch failed with 403 FORBIDDEN. Retrying using Playwright fallback...")
            html, status, error, final_url = await self.fallback_fetcher.fetch(url)
            if not error and html:
                logger.info(f"Playwright fallback succeeded for {url}")
        
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
            canonical_url=extracted.get("canonical_url"),
            headings=extracted.get("headings", []),
            content=extracted.get("content", ""),
            topics=topics,
            links=extracted.get("links", []),
            images=extracted.get("images", []),
            status_code=status,
            error=None
        )
