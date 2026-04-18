from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any

class ImageMeta(BaseModel):
    src: str
    alt: Optional[str] = None

class CrawledData(BaseModel):
    url: str
    domain: str
    page_type: str = "other"  # article, product, category/list, homepage, other
    title: Optional[str] = None
    description: Optional[str] = None
    headings: List[str] = Field(default_factory=list)
    content: str = ""
    topics: List[str] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)
    images: List[ImageMeta] = Field(default_factory=list)
    
    # Metadata about the fetch itself
    status_code: int = 200
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    status_code: int = 500
    url: Optional[str] = None
    detail: Optional[str] = None
