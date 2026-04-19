from pydantic import BaseModel, Field
from typing import Optional

class ImageMeta(BaseModel):
    src: str
    alt: Optional[str] = None

class CrawledData(BaseModel):
    url: str
    domain: str
    page_type: str = "other"  # article, product, category/list, homepage, challenge, other
    title: Optional[str] = None
    description: Optional[str] = None
    canonical_url: Optional[str] = None
    headings: list[str] = Field(default_factory=list)
    content: str = ""
    topics: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    images: list[ImageMeta] = Field(default_factory=list)
    
    # Metadata about the fetch itself
    status_code: int = 200
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    status_code: int = 500
    url: Optional[str] = None
    detail: Optional[str] = None
