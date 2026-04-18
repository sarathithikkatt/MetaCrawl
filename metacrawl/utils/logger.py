import logging
import sys
from metacrawl.config.settings import settings

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger based on the application settings."""
    logger = logging.getLogger(name)
    
    # Only configure if it hasn't been configured yet to avoid duplicate logs
    if not logger.handlers:
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(level)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.propagate = False
        
    return logger
