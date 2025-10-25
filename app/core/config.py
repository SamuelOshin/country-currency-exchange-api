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
        """
        Get absolute cache directory path
        
        In production environments (e.g., Leapcell, Docker), use /tmp
        since the main filesystem is often read-only
        """
        # Use /tmp in production for read-only file systems
        if self.ENVIRONMENT == "production":
            return "/tmp/cache"
        return os.path.abspath(self.CACHE_DIR)

settings = Settings()

# Ensure cache directory exists (with error handling for read-only fs)
try:
    os.makedirs(settings.cache_path, exist_ok=True)
except OSError as e:
    # If cache directory creation fails, try /tmp as fallback
    if not os.path.exists("/tmp/cache"):
        os.makedirs("/tmp/cache", exist_ok=True)