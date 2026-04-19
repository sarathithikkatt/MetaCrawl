import pytest
from metacrawl.extractors import BasicExtractor, TrafilaturaExtractor

SAMPLE_HTML = """
<html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="A test page description">
        <link rel="canonical" href="https://example.com/canonical">
    </head>
    <body>
        <h1>Heading 1</h1>
        <h2>Heading 2</h2>
        <p>This is some <b>main content</b>.</p>
        <a href="/relative/link">Relative Link</a>
        <a href="https://other.com/absolute">Absolute Link</a>
        <img src="test.jpg" alt="Test Image">
    </body>
</html>
"""

def test_basic_extractor():
    extractor = BasicExtractor()
    result = extractor.extract(SAMPLE_HTML, "https://example.com/start")
    
    assert result["title"] == "Test Page"
    assert result["description"] == "A test page description"
    assert result["canonical_url"] == "https://example.com/canonical"
    assert "Heading 1" in result["headings"]
    assert "Heading 2" in result["headings"]
    assert "This is some" in result["content"]
    assert "main content" in result["content"]
    assert "https://example.com/relative/link" in result["links"]
    assert "https://other.com/absolute" in result["links"]
    assert len(result["images"]) == 1
    assert result["images"][0]["src"] == "https://example.com/test.jpg"
    assert result["images"][0]["alt"] == "Test Image"

def test_trafilatura_extractor():
    extractor = TrafilaturaExtractor()
    result = extractor.extract(SAMPLE_HTML, "https://example.com/start")
    
    assert result["title"] == "Test Page"
    assert result["description"] == "A test page description"
    # Trafilatura's extract might return different content formatting, but it should still find the main text
    assert "This is some" in result["content"]
    assert "main content" in result["content"]
    assert "https://example.com/relative/link" in result["links"]
