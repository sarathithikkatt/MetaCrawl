from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    # HTTP Settings
    timeout: int = 15
    max_retries: int = 3
    user_agent: str = "MetaCrawl/2.0"
    
    # Feature toggles
    use_playwright_fallback: bool = True
    playwright_timeout: int = 30
    headless: bool = True
    
    # Extractor choice
    extractor_type: Literal["trafilatura", "basic"] = "trafilatura"
    
    # Topic extractor choice
    topic_model: Literal["tfidf", "yake"] = "tfidf"
    
    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_prefix="METACRAWL_", env_file=".env", env_file_encoding="utf-8")

settings = Settings()
