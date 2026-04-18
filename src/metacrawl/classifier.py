import re
from typing import Dict, Any
from .interfaces import ClassifierABC

class HeuristicClassifier(ClassifierABC):
    def classify(self, extracted_data: Dict[str, Any]) -> str:
        content = extracted_data.get("content", "") or ""
        headings = extracted_data.get("headings", [])
        title = extracted_data.get("title", "") or ""
        links = extracted_data.get("links", [])
        
        content_lower = content.lower()
        title_lower = title.lower()
        all_headings = " ".join(headings).lower()
        
        # Product heuristics
        product_keywords = ["add to cart", "buy now", "in stock", "add to basket", "sku", "shipping"]
        product_score = sum(1 for kw in product_keywords if kw in content_lower or kw in all_headings)
        
        if product_score >= 2 or ("cart" in title_lower) or ("price" in title_lower):
            return "product"
            
        # Homepage heuristics
        # Typically homepages have little deep content, many links, and titles like "Home" or "Welcome"
        if len(content) < 1000 and len(links) > 20:
            if "home" in title_lower or "welcome" in title_lower or "official site" in title_lower:
                return "homepage"
                
        # List/Category heuristics
        # High link-to-text density usually indicates a category index
        list_keywords = ["category", "index", "all products", "latest posts"]
        list_score = sum(1 for kw in list_keywords if kw in title_lower or kw in all_headings)
        if len(links) > 15 and len(content) < 2000 and (list_score > 0 or len(links) / (len(content) + 1) > 0.05):
            return "category/list"
            
        # Article heuristics
        # Long coherent text, author info, published dates
        article_keywords = ["published", "read time"]
        article_score = sum(1 for kw in article_keywords if kw in content_lower[:1000])
        
        if len(content) > 1500 or article_score > 0:
            return "article"
            
        return "other"
