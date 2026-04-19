from abc import ABC, abstractmethod
from typing import Any

class BaseExtractor(ABC):
    """
    Abstract interface for parsing and extracting structured data 
    and main content from HTML.
    """
    @abstractmethod
    def extract(self, html: str, url: str) -> dict[str, Any]:
        """
        Extract content from HTML.
        
        :param html: Raw HTML string
        :param url: The base URL, useful for resolving relative links
        :return: Dictionary with keys corresponding to the Extracted fields.
        """
        pass
