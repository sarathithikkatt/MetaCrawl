from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urljoin
from typing import Any
from .base import BaseExtractor
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

class TrafilaturaExtractor(BaseExtractor):
    def extract(self, html: str, url: str) -> dict[str, Any]:
        logger.debug(f"Starting trafilatura extraction for {url}")
        soup = BeautifulSoup(html, "lxml")
        
        # Extract title
        title = None
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        if not title:
            logger.warning(f"No <title> found for {url}")
            
        # Extract description
        description = None
        meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc.get("content", "").strip()
        else:
            logger.debug(f"No meta description found for {url}")

        # Extract canonical URL
        canonical_tag = soup.find("link", rel="canonical")
        canonical_url = urljoin(url, canonical_tag["href"].strip()) if canonical_tag and canonical_tag.get("href") else None
            
        # Extract headings
        headings: list[str] = []
        for tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(tag):
                text = h.get_text(strip=True)
                if text:
                    headings.append(text)
                    
        # Extract main content
        content = trafilatura.extract(html, include_links=False, include_images=False, include_formatting=False)
        if not content:
            logger.warning(f"Trafilatura failed to extract main content for {url}, falling back to simple text")
            # Fallback to simple text extraction if trafilatura fails
            content = soup.get_text(separator="\n", strip=True)
            
        # Extract links
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href.startswith("javascript:") and not href.startswith("mailto:") and not href.startswith("#"):
                absolute_url = urljoin(url, href)
                links.add(absolute_url)
                
        # Extract images
        images: list[dict[str, str]] = []
        for img in soup.find_all("img", src=True):
            if "src" in img.attrs:
                src = urljoin(url, img["src"].strip())
                alt = img.get("alt", "").strip() or None
                images.append({"src": src, "alt": alt})
        
        logger.debug(f"Extracted {len(headings)} headings, {len(links)} links, {len(images)} images for {url}")
            
        return {
            "title": title,
            "description": description,
            "canonical_url": canonical_url,
            "headings": headings,
            "content": content,
            "links": list(links),
            "images": images
        }
