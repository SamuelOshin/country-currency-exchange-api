from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    SSL_CERT_PATH: Optional[str] = "ca.pem"
    SSL_VERIFY: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # External APIs
    RESTCOUNTRIES_API_URL: str
    EXCHANGE_API_URL: str
    
    # API Configuration
    API_TIMEOUT: int = 30
    CACHE_DIR: str = "app/cache"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def cache_path(self) -> str:
        """Get absolute cache directory path"""
        return os.path.abspath(self.CACHE_DIR)

settings = Settings()

# Ensure cache directory exists
os.makedirs(settings.cache_path, exist_ok=True)