from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Server settings
    # Render sets PORT environment variable automatically
    HOST: str = "0.0.0.0"
    PORT: int = 8000  # Will be overridden by Render's PORT env var
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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override PORT from environment if set (Render sets this)
        port_env = os.getenv("PORT")
        if port_env:
            self.PORT = int(port_env)


settings = Settings()

