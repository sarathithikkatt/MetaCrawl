from abc import ABC, abstractmethod
from typing import Tuple, Optional

class BaseFetcher(ABC):
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
