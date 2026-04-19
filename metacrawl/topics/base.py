from abc import ABC, abstractmethod

class BaseTopicExtractor(ABC):
    """
    Abstract interface for extracting key topics from raw text.
    """
    @abstractmethod
    def extract_topics(self, text: str, max_topics: int = 5) -> list[str]:
        """
        Extract topics from the main content.
        
        :param text: Cleaned main body text.
        :param max_topics: Maximum number of topics to return.
        :return: List of topic strings.
        """
        pass
