import pytest
from metacrawl.topics.tfidf_extractor import TFIDFTopicExtractor

def test_tfidf_topic_extractor():
    extractor = TFIDFTopicExtractor()
    
    # Needs enough words for TF-IDF to work properly
    text = "The quick brown fox jumps over the lazy dog. The fox is quick and brown. The dog is lazy and sleeps all day."
    # TfidfVectorizer requires more words than this for meaningful results, but let's see.
    # Actually, TfidfVectorizer with a single document will just return all words that aren't stop words.
    
    topics = extractor.extract_topics(text, max_topics=3)
    
    assert len(topics) <= 3
    # Check for expected words (excluding stop words)
    # The words 'fox', 'quick', 'brown', 'lazy', 'dog', 'jumps', 'sleeps' are all candidates.
    assert "fox" in topics or "dog" in topics or "lazy" in topics

def test_tfidf_topic_extractor_short_text():
    extractor = TFIDFTopicExtractor()
    text = "Too short."
    topics = extractor.extract_topics(text)
    assert topics == []

def test_tfidf_topic_extractor_empty_text():
    extractor = TFIDFTopicExtractor()
    assert extractor.extract_topics("") == []
    assert extractor.extract_topics(None) == []
