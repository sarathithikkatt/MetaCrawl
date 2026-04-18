from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from .models import CrawledData

class FetcherABC(ABC):
    """
    Abstract interface for fetching webpage contents.
    """
    @abstractmethod
    async def fetch(self, url: str) -> Tuple[Optional[str], int, Optional[str], str]:
        """
        Fetch the URL content.
        
        :param url: The target URL
        :return: Tuple of (raw_html_body, status_code, error_message, final_url)
        """
        pass

class ExtractorABC(ABC):
    """
    Abstract interface for parsing and extracting structured data 
    and main content from HTML.
    """
    @abstractmethod
    def extract(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract content from HTML.
        
        :param html: Raw HTML string
        :param url: The base URL, useful for resolving relative links
        :return: Dictionary with keys corresponding to the Extracted fields.
        """
        pass

class ClassifierABC(ABC):
    """
    Abstract interface for page type classification.
    """
    @abstractmethod
    def classify(self, extracted_data: Dict[str, Any]) -> str:
        """
        Classifies the page type based on extracted data.
        
        :param extracted_data: Dictionary of extracted HTML features.
        :return: string page type (e.g. article, product, etc.)
        """
        pass

class TopicExtractorABC(ABC):
    """
    Abstract interface for extracting key topics from raw text.
    """
    @abstractmethod
    def extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """
        Extract topics from the main content.
        
        :param text: Cleaned main body text.
        :param max_topics: Maximum number of topics to return.
        :return: List of topic strings.
        """
        pass
