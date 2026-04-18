from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urljoin
from typing import Dict, Any, List
from .interfaces import ExtractorABC

class HTMLExtractor(ExtractorABC):
    def extract(self, html: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        
        # Extract title
        title = None
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            
        # Extract description
        description = None
        meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc.get("content", "").strip()
            
        # Extract headings
        headings: List[str] = []
        for tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(tag):
                text = h.get_text(strip=True)
                if text:
                    headings.append(text)
                    
        # Extract main content
        content = trafilatura.extract(html, include_links=False, include_images=False, include_formatting=False)
        if not content:
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
        images: List[Dict[str, str]] = []
        for img in soup.find_all("img", src=True):
            src = urljoin(url, img["src"].strip())
            alt = img.get("alt", "").strip() or None
            images.append({"src": src, "alt": alt})
            
        return {
            "title": title,
            "description": description,
            "headings": headings,
            "content": content,
            "links": list(links),
            "images": images
        }
