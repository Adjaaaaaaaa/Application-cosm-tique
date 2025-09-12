"""
Configuration settings for backend services.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).resolve().parent.parent.parent / '.env')

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# API Configuration
API_TITLE = "BeautyScan API"
API_DESCRIPTION = "API for BeautyScan cosmetic analysis platform"
API_VERSION = "v1"

# Server Configuration
HOST = "127.0.0.1"
PORT = 8000
DEBUG = True
LOG_LEVEL = "INFO"

# CORS Configuration
CORS_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# Azure OpenAI Configuration
AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")  # From .env file
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get("OPENAI_MODEL", "gpt-4")  # From .env file

# OpenFact Beauty Configuration
OPENFACT_BEAUTY_API_KEY = os.environ.get("OPENFACT_BEAUTY_API_KEY", "")
OPENBEAUTYFACTS_API_URL = os.environ.get("OPENBEAUTYFACTS_API_URL", "https://world.openbeautyfacts.org/cgi/search.pl")

# PubChem Configuration
PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PUBCHEM_API_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# Settings class for compatibility
class Settings:
    """Settings class for backend services."""
    
    def __init__(self):
        self.API_TITLE = API_TITLE
        self.API_DESCRIPTION = API_DESCRIPTION
        self.API_VERSION = API_VERSION
        self.HOST = HOST
        self.PORT = PORT
        self.DEBUG = DEBUG
        self.LOG_LEVEL = LOG_LEVEL
        self.CORS_ORIGINS = CORS_ORIGINS
        self.AZURE_OPENAI_KEY = AZURE_OPENAI_KEY
        self.AZURE_OPENAI_ENDPOINT = AZURE_OPENAI_ENDPOINT
        self.AZURE_OPENAI_API_VERSION = AZURE_OPENAI_API_VERSION
        self.AZURE_OPENAI_DEPLOYMENT_NAME = AZURE_OPENAI_DEPLOYMENT_NAME
        self.OPENFACT_BEAUTY_API_KEY = OPENFACT_BEAUTY_API_KEY
        self.OPENBEAUTYFACTS_API_URL = OPENBEAUTYFACTS_API_URL
        self.PUBCHEM_BASE_URL = PUBCHEM_BASE_URL
        self.PUBCHEM_API_URL = PUBCHEM_API_URL

# Global settings instance
settings = Settings()
