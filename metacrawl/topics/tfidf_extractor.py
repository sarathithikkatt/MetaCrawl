from sklearn.feature_extraction.text import TfidfVectorizer
from .base import BaseTopicExtractor
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

class TFIDFTopicExtractor(BaseTopicExtractor):
    def extract_topics(self, text: str, max_topics: int = 5) -> list[str]:
        if not text or len(text.split()) < 10:
            logger.warning(f"Text too short for topic extraction ({len((text or '').split())} words), skipping")
            return []
            
        try:
            logger.debug(f"Running TF-IDF topic extraction (max_topics={max_topics}, text_words={len(text.split())})")
            vectorizer = TfidfVectorizer(stop_words='english', max_features=max_topics * 3, ngram_range=(1, 2))
            X = vectorizer.fit_transform([text])
            
            feature_names = vectorizer.get_feature_names_out()
            scores = X.toarray()[0]
            logger.debug(f"TF-IDF vectorizer produced {len(feature_names)} features")
            
            top_indices = scores.argsort()[::-1]
            
            topics = [feature_names[i] for i in top_indices[:max_topics]]
            logger.debug(f"Extracted topics: {topics}")
            return topics
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}", exc_info=True)
            return []
