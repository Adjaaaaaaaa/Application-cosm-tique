"""
Base settings for BeautyScan project.

This module contains the core Django configuration that is shared between
development and production environments. It defines the fundamental structure
of the application including installed apps, middleware, authentication,
and external service configurations.

The settings are organized to separate Django core apps, third-party apps,
and local project apps for better maintainability and clarity.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# This ensures consistent path resolution across different environments
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Charger les variables d'environnement depuis le fichier .env
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
# Import centralized environment configuration
from config.env import SECRET_KEY, DEBUG, DJANGO_SETTINGS_MODULE
from config.env import is_development_mode, is_production_mode, get_database_config
from config.env import ALLOWED_HOSTS, AUTHORIZED_DEV_USERS
from config.env import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, OLLAMA_API_URL

# Azure OpenAI Configuration
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4.1')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
from config.env import STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY
from config.env import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS

# Application definition
# Django core apps provide essential functionality like admin, auth, sessions
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Third-party apps extend Django with additional functionality
# CORS headers for cross-origin requests
THIRD_PARTY_APPS = [
    'corsheaders',
]

# Local project apps contain the business logic specific to BeautyScan
# Organized by functionality: accounts, scans, payments, AI features
LOCAL_APPS = [
    'common',  # Shared utilities and common functionality
    'core',  # Clean Architecture domain layer
    'apps.accounts',  # User management and authentication
    'apps.scans',  # Product scanning and analysis
    'apps.api',  # Internal and external API endpoints
    'apps.payments',  # Subscription and payment processing
    'apps.ai_routines',  # AI-powered skincare routines
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware provides request/response processing pipeline
# Order matters: security first, then session/auth, then content processing
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Security headers and HTTPS redirects
    'django.contrib.sessions.middleware.SessionMiddleware',  # Session management
    'corsheaders.middleware.CorsMiddleware',  # Cross-origin resource sharing
    'django.middleware.common.CommonMiddleware',  # URL processing and logging
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # User authentication
    'django.contrib.messages.middleware.MessageMiddleware',  # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection

]

ROOT_URLCONF = 'config.urls'

# Template configuration for rendering HTML pages
# Custom context processor injects Premium status into all templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Global template directory
        'APP_DIRS': True,  # Allow app-specific template directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'common.context_processors.premium_status',  # Custom Premium status injection
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation ensures strong user passwords
# Multiple validators check different aspects of password strength
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization - Disabled for French-only application
# This simplifies the application by removing i18n overhead
USE_I18N = False
USE_L10N = False

# Default language for the application
LANGUAGE_CODE = 'fr'

# Static files configuration for CSS, JavaScript, and images
# All static files are collected in the staticfiles directory
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Production static files collection

# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Database configuration
# Uses centralized configuration from config.env
DATABASES = {
    'default': get_database_config()
}

# Media files for user-uploaded content
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type for models
# BigAutoField provides larger range than AutoField for scalability
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# API INTERNE - SÉCURITÉ
# =============================================================================
# Token d'authentification pour l'API interne (services internes uniquement)
INTERNAL_API_TOKEN = 'internal_beautyscan_2024'

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'fr-FR'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_TZ = True

# Authentication URLs for login/logout flow
# These URLs are used by Django's authentication system
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'  # Redirect to home page after login
LOGOUT_REDIRECT_URL = '/'  # Redirect to home page after logout

# REST Framework configuration removed - not used in current application



# Email backend (dev): afficher les emails dans la console
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS settings for cross-origin requests
# Allows frontend applications to communicate with the API
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]

# External API configuration
# These services provide product data, AI capabilities, and payment processing
OPENBEAUTYFACTS_API_URL = "https://world.openbeautyfacts.org/api/v0"  # Product database
PUBCHEM_API_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"  # Chemical information
