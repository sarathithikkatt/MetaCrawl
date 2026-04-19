import pytest
from metacrawl.classifiers.heuristic_classifier import HeuristicClassifier

def test_amazon_challenge_detection():
    classifier = HeuristicClassifier()
    
    # Mock data based on user input
    amazon_challenge_data = {
        "url": "https://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster",
        "title": "Amazon.com",
        "content": "Click the button below to continue shopping\nContinue shopping\nConditions of Use\nPrivacy Policy\n© 1996-2025, Amazon.com, Inc. or its affiliates",
        "headings": [],
        "links": [
            "https://www.amazon.com/gp/help/customer/display.html/ref=footer_cou?ie=UTF8&nodeId=508088",
            "https://www.amazon.com/gp/help/customer/display.html/ref=footer_privacy?ie=UTF8&nodeId=468496"
        ]
    }
    
    result = classifier.classify(amazon_challenge_data)
    assert result == "challenge"

def test_generic_challenge_detection():
    classifier = HeuristicClassifier()
    
    generic_challenge_data = {
        "url": "https://example.com/some-page",
        "title": "Access Denied",
        "content": "Please verify you are a human. We have detected automation tools.",
        "headings": ["Security Check"],
        "links": []
    }
    
    result = classifier.classify(generic_challenge_data)
    assert result == "challenge"

def test_product_detection():
    classifier = HeuristicClassifier()
    
    product_data = {
        "url": "https://example.com/product/123",
        "title": "Cool Toaster",
        "content": "This is a great toaster. Buy now and add to cart. In stock.",
        "headings": ["Product Description"],
        "links": []
    }
    
    result = classifier.classify(product_data)
    assert result == "product"
