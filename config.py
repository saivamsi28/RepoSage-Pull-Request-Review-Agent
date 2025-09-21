import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration class with validation and defaults"""
    
    # GitHub Configuration
    github_token: str
    repo_owner: Optional[str] = None
    repo_name: Optional[str] = None
    pr_number: Optional[str] = None
    
    # AI Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-flash"
    max_tokens: int = 8000
    
    # Application Configuration
    debug_mode: bool = False
    port: int = 5000
    host: str = "127.0.0.1"
    
    # Rate Limiting
    rate_limit_requests: int = 10
    rate_limit_window_minutes: int = 1
    
    # Security
    max_diff_size: int = 50000  # 50KB
    request_timeout: int = 30  # seconds
    
    # Logging
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_required_fields()
        self._setup_logging()
    
    def _validate_required_fields(self):
        """Validate required configuration fields"""
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        if self.max_diff_size <= 0:
            raise ValueError("MAX_DIFF_SIZE must be positive")
        
        if self.request_timeout <= 0:
            raise ValueError("REQUEST_TIMEOUT must be positive")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR
        }
        
        level = log_levels.get(self.log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

def load_config() -> Config:
    """Load and return application configuration"""
    return Config(
        # GitHub
        github_token=os.getenv("GITHUB_TOKEN", ""),
        repo_owner=os.getenv("REPO_OWNER"),
        repo_name=os.getenv("REPO_NAME"),
        pr_number=os.getenv("PR_NUMBER"),
        
        # AI
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        max_tokens=int(os.getenv("MAX_TOKENS", "8000")),
        
        # App
        debug_mode=os.getenv("DEBUG", "False").lower() == "true",
        port=int(os.getenv("PORT", "5000")),
        host=os.getenv("HOST", "127.0.0.1"),
        
        # Rate limiting
        rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "10")),
        rate_limit_window_minutes=int(os.getenv("RATE_LIMIT_WINDOW_MINUTES", "1")),
        
        # Security
        max_diff_size=int(os.getenv("MAX_DIFF_SIZE", "50000")),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
        
        # Logging
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )

# Global configuration instance
try:
    config = load_config()
    
    # Legacy compatibility (for existing code)
    GITHUB_TOKEN = config.github_token
    REPO_OWNER = config.repo_owner
    REPO_NAME = config.repo_name
    PR_NUMBER = config.pr_number
    GEMINI_API_KEY = config.gemini_api_key
    DEBUG_MODE = config.debug_mode
    PORT = config.port
    
except Exception as e:
    logger.error(f"Configuration error: {e}")
    raise