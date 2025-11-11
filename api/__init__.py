from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    MAX_SEARCH_RESULTS: int = 100
    DEFAULT_SEARCH_LIMIT: int = 50
    DEFAULT_PICKUP_DISTANCE: int = 50
    
    # Rate limiting (requests per minute)
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Cache settings
    ENABLE_CACHE: bool = True
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

