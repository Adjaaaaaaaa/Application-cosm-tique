"""
Configuration settings for backend services.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
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


# =============================================================================
# SERVICE CONFIGURATION CLASSES
# =============================================================================

class ServiceConfig:
    """Configuration centralisée pour tous les services."""
    
    # Configuration des APIs externes
    API_CONFIGS = {
        'openbeautyfacts': {
            'base_url': 'https://world.openbeautyfacts.org/api/v0',
            'timeout': 10,
            'cache_ttl': 3600,  # 1 heure
            'user_agent': 'BeautyScan/1.0 (https://beautyscan.com)'
        },
        'pubchem': {
            'base_url': 'https://pubchem.ncbi.nlm.nih.gov/rest/pug',
            'timeout': 15,
            'cache_ttl': 86400,  # 24 heures
            'user_agent': 'BeautyScan/1.0 (https://beautyscan.com)'
        },
        'azure_openai': {
            'timeout': 30,
            'max_tokens': 2000,
            'temperature': 0.7
        },
        'azure_search': {
            'timeout': 10,
            'max_results': 5
        }
    }
    
    # Configuration des services internes
    INTERNAL_CONFIGS = {
        'product_database': {
            'cache_size': 1000,
            'cache_ttl': 7200,  # 2 heures
            'max_retries': 3
        },
        'image_analysis': {
            'max_image_size': 5 * 1024 * 1024,  # 5MB
            'supported_formats': ['jpg', 'jpeg', 'png', 'webp'],
            'timeout': 20
        },
        'ingredient_analysis': {
            'max_ingredients': 50,
            'batch_size': 10,
            'timeout': 60
        }
    }
    
    # Configuration des scores et seuils
    SCORING_CONFIGS = {
        'safety_score': {
            'excellent_threshold': 75,
            'good_threshold': 50,
            'poor_threshold': 25,
            'min_score': 0,
            'max_score': 100
        },
        'h_codes': {
            'category_1_weight': 3.0,
            'category_2_weight': 1.5,
            'category_3_weight': 0.5,
            'health_factor': 2.0,
            'physical_factor': 1.5,
            'environment_factor': 0.5
        }
    }
    
    @classmethod
    def get_api_config(cls, service_name: str) -> Dict[str, Any]:
        """Récupère la configuration d'une API externe."""
        config = cls.API_CONFIGS.get(service_name, {})
        
        # Override avec les variables d'environnement si disponibles
        env_key = f"{service_name.upper()}_API_URL"
        if hasattr(settings, env_key):
            config['base_url'] = getattr(settings, env_key)
        
        return config
    
    @classmethod
    def get_internal_config(cls, service_name: str) -> Dict[str, Any]:
        """Récupère la configuration d'un service interne."""
        return cls.INTERNAL_CONFIGS.get(service_name, {})
    
    @classmethod
    def get_scoring_config(cls, config_type: str) -> Dict[str, Any]:
        """Récupère la configuration de scoring."""
        return cls.SCORING_CONFIGS.get(config_type, {})
    
    @classmethod
    def is_service_enabled(cls, service_name: str) -> bool:
        """Vérifie si un service est activé."""
        # Vérifier les variables d'environnement
        env_key = f"{service_name.upper()}_ENABLED"
        if hasattr(settings, env_key):
            return getattr(settings, env_key, True)
        
        # Services activés par défaut
        enabled_by_default = [
            'openbeautyfacts', 'pubchem', 'product_database',
            'image_analysis', 'ingredient_analysis'
        ]
        
        return service_name in enabled_by_default


class ServiceHealth:
    """Gestion de la santé des services."""
    
    @staticmethod
    def check_service_health(service_name: str) -> Dict[str, Any]:
        """Vérifie la santé d'un service."""
        try:
            # Vérifier si le service est activé
            if not ServiceConfig.is_service_enabled(service_name):
                return {
                    'status': 'disabled',
                    'message': f'Service {service_name} is disabled',
                    'healthy': False
                }
            
            # Vérifier la configuration
            config = ServiceConfig.get_api_config(service_name)
            if not config:
                return {
                    'status': 'misconfigured',
                    'message': f'No configuration found for {service_name}',
                    'healthy': False
                }
            
            return {
                'status': 'healthy',
                'message': f'Service {service_name} is healthy',
                'healthy': True,
                'config': config
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error checking {service_name}: {str(e)}',
                'healthy': False
            }
    
    @staticmethod
    def get_all_services_health() -> Dict[str, Dict[str, Any]]:
        """Vérifie la santé de tous les services."""
        services = [
            'openbeautyfacts', 'pubchem', 'azure_openai', 'azure_search',
            'product_database', 'image_analysis', 'ingredient_analysis'
        ]
        
        health_status = {}
        for service in services:
            health_status[service] = ServiceHealth.check_service_health(service)
        
        return health_status


# Configuration globale
SERVICE_CONFIG = ServiceConfig()
SERVICE_HEALTH = ServiceHealth()
