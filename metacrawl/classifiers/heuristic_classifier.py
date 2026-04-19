from typing import Any
from .base import BaseClassifier
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

class HeuristicClassifier(BaseClassifier):
    def classify(self, extracted_data: dict[str, Any]) -> str:
        content = extracted_data.get("content", "") or ""
        headings = extracted_data.get("headings", [])
        title = extracted_data.get("title", "") or ""
        links = extracted_data.get("links", [])

        logger.debug(
            f"Classifying page: title='{title[:60]}', content_len={len(content)}, "
            f"links={len(links)}, headings={len(headings)}"
        )
        
        content_lower = content.lower()
        title_lower = title.lower()
        all_headings = " ".join(headings).lower()
        
        # Challenge/Bot detection heuristics
        challenge_keywords = [
             "continue shopping", 
             "bot detection", 
             "captcha", 
             "robot check", 
             "not a robot",
             "verify you are a human",
             "access denied",
             "automation tools",
             "checking your browser",
             "enable javascript and cookies to continue"
         ]
        if any(kw in content_lower for kw in challenge_keywords) or \
            (url := extracted_data.get("url", "")) and "amazon" in url.lower() and "continue shopping" in content_lower:
             logger.debug(f"Classified as 'challenge' — bot detection detected")
             return "challenge"

        # Product heuristics
        product_keywords = ["add to cart", "buy now", "in stock", "add to basket", "sku", "shipping"]
        product_score = sum(1 for kw in product_keywords if kw in content_lower or kw in all_headings)
        
        if product_score >= 2 or ("cart" in title_lower) or ("price" in title_lower):
            logger.debug(f"Classified as 'product' (product_score={product_score})")
            return "product"
            
        # Homepage heuristics
        if len(content) < 1000 and len(links) > 20:
            if "home" in title_lower or "welcome" in title_lower or "official site" in title_lower:
                logger.debug(f"Classified as 'homepage' (content_len={len(content)}, links={len(links)})")
                return "homepage"
                
        # List/Category heuristics
        list_keywords = ["category", "index", "all products", "latest posts"]
        list_score = sum(1 for kw in list_keywords if kw in title_lower or kw in all_headings)
        if len(links) > 15 and len(content) < 2000 and (list_score > 0 or len(links) / (len(content) + 1) > 0.05):
            logger.debug(f"Classified as 'category/list' (list_score={list_score}, links={len(links)})")
            return "category/list"
            
        # Article heuristics
        article_keywords = ["published", "read time"]
        article_score = sum(1 for kw in article_keywords if kw in content_lower[:1000])
        
        if len(content) > 1500 or article_score > 0:
            logger.debug(f"Classified as 'article' (article_score={article_score}, content_len={len(content)})")
            return "article"
            
        logger.debug(f"Classified as 'other' — no heuristic matched")
        return "other"
