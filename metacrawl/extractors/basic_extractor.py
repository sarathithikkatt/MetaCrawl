from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, Any, List
from .base import BaseExtractor

class BasicExtractor(BaseExtractor):
    def extract(self, html: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        
        meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        description = meta_desc.get("content", "").strip() if meta_desc and meta_desc.get("content") else None
            
        headings: List[str] = []
        for tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(tag):
                if text := h.get_text(strip=True):
                    headings.append(text)
                    
        # Basic content: just dump everything
        content = soup.get_text(separator="\n", strip=True)
            
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href.startswith("javascript:") and not href.startswith("mailto:") and not href.startswith("#"):
                links.add(urljoin(url, href))
                
        images: List[Dict[str, str]] = []
        for img in soup.find_all("img", src=True):
            if "src" in img.attrs:
                images.append({
                    "src": urljoin(url, img["src"].strip()),
                    "alt": img.get("alt", "").strip() or None
                })
            
        return {
            "title": title,
            "description": description,
            "headings": headings,
            "content": content,
            "links": list(links),
            "images": images
        }
