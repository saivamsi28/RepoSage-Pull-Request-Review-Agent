# config.py
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class Config:
    """
    Application configuration class.
    Loads settings from environment variables and provides centralized access.
    """
    def __init__(self):
        self.GIT_SERVICE_TOKEN = os.getenv("GIT_SERVICE_TOKEN")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        
        self.REPO_OWNER = os.getenv("REPO_OWNER")
        self.REPO_NAME = os.getenv("REPO_NAME")
        self.PR_NUMBER = os.getenv("PR_NUMBER")
        
        self.MAX_DIFF_SIZE = int(os.getenv("MAX_DIFF_SIZE", 50000))
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
        
        self._validate()
        self._setup_logging()

    def _validate(self):
        """Ensures that critical configuration variables are set."""
        if not self.GIT_SERVICE_TOKEN:
            raise ValueError("Configuration Error: GIT_SERVICE_TOKEN is not set in the .env file.")
        if not self.GEMINI_API_KEY:
            raise ValueError("Configuration Error: GEMINI_API_KEY is not set in the .env file.")

    def _setup_logging(self):
        """Sets up the basic logging configuration for the application."""
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

try:
    config = Config()
except ValueError as e:
    logging.getLogger(__name__).error(f"Failed to load configuration: {e}")
    raise