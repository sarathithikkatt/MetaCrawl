from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from .interfaces import TopicExtractorABC

class TFIDFTopicExtractor(TopicExtractorABC):
    def extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        if not text or len(text.split()) < 10:
            return []
            
        try:
            # We use unigrams and bigrams
            vectorizer = TfidfVectorizer(stop_words='english', max_features=max_topics * 3, ngram_range=(1, 2))
            X = vectorizer.fit_transform([text])
            
            # Get feature names and their tf-idf scores
            feature_names = vectorizer.get_feature_names_out()
            scores = X.toarray()[0]
            
            # Sort features by score in descending order
            top_indices = scores.argsort()[::-1]
            
            # Return the top 'max_topics' features
            topics = [feature_names[i] for i in top_indices[:max_topics]]
            return topics
        except Exception as e:
            print(f"Topic extraction failed: {e}")
            return []
