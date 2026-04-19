from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Any
from .base import BaseExtractor
from metacrawl.utils.logger import get_logger

logger = get_logger(__name__)

class BasicExtractor(BaseExtractor):
    def extract(self, html: str, url: str) -> dict[str, Any]:
        logger.debug(f"Starting basic extraction for {url}")
        soup = BeautifulSoup(html, "lxml")
        
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        if not title:
            logger.warning(f"No <title> found for {url}")
        
        meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        description = meta_desc.get("content", "").strip() if meta_desc and meta_desc.get("content") else None
        
        canonical_tag = soup.find("link", rel="canonical")
        canonical_url = urljoin(url, canonical_tag["href"].strip()) if canonical_tag and canonical_tag.get("href") else None
            
        headings: list[str] = []
        for tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(tag):
                if text := h.get_text(strip=True):
                    headings.append(text)

        content = soup.get_text(separator="\n", strip=True)
        if not content:
            logger.warning(f"No text content extracted for {url}")
            
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href.startswith("javascript:") and not href.startswith("mailto:") and not href.startswith("#"):
                links.add(urljoin(url, href))
                
        images: list[dict[str, str]] = []
        for img in soup.find_all("img", src=True):
            if "src" in img.attrs:
                images.append({
                    "src": urljoin(url, img["src"].strip()),
                    "alt": img.get("alt", "").strip() or None
                })

        logger.debug(f"Basic extraction complete for {url}: {len(headings)} headings, {len(links)} links, {len(images)} images")
            
        return {
            "title": title,
            "description": description,
            "canonical_url": canonical_url,
            "headings": headings,
            "content": content,
            "links": list(links),
            "images": images
        }
