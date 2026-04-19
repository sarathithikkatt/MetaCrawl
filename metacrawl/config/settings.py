from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    # HTTP Settings
    timeout: int = 15
    max_retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    rate_limit_delay: float = 1.0  # Seconds between requests to the same domain
    
    # Feature toggles
    check_robots_txt: bool = True
    use_playwright_fallback: bool = True
    playwright_timeout: int = 30
    headless: bool = True
    
    # Extractor choice
    extractor_type: Literal["trafilatura", "basic"] = "trafilatura"
    
    # Topic extractor choice
    topic_model: Literal["tfidf", "yake"] = "tfidf"
    
    # Logging
    log_level: str = "INFO"
    log_dir: str = "logs"

    model_config = SettingsConfigDict(env_prefix="METACRAWL_", env_file=".env", env_file_encoding="utf-8")

settings = Settings()
