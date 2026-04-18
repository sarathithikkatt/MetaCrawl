from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseClassifier(ABC):
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
