"""
Development settings for BeautyScan project.

This module contains Django configuration specific to development environments.
It enables debugging, uses local database, and provides a secure Premium dev mode
that allows authorized developers to test Premium features without payment.

The Premium dev mode is a critical security feature that must only be enabled
in controlled development environments to prevent unauthorized access to Premium features.
"""

import os
import sys
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
# Debug mode provides detailed error pages and development tools
# This should NEVER be enabled in production for security reasons
DEBUG = True

# Allowed hosts for development server
# Restricts which hostnames can serve the application
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# Database configuration for development
# Uses centralized configuration from config.env
# Falls back to SQLite for local development if no Azure database is configured
DATABASES = {
    'default': get_database_config()
}

# Email backend for development
# Sends emails to console instead of actual email servers
# This prevents accidental emails during development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging configuration for development
# Provides console output for debugging and monitoring
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Premium Development Mode Configuration
# This is a critical security feature that allows authorized developers
# to test Premium features without going through payment verification
# 
# SECURITY CONSIDERATIONS:
# - Only enabled in development environments
# - Requires virtual environment for additional security
# - Limited to specific authorized users only
# - Never enabled in production

# AI Service Configuration
# Configuration for AI services (Ollama, OpenAI, etc.)
# These settings control which AI service to use for Premium features

# Ollama Configuration (Local AI)
# Uncomment and configure if using Ollama for local AI processing
# OLLAMA_URL = 'http://localhost:11434'
# OLLAMA_MODEL = 'llama3.2'

# OpenAI Configuration (External AI)
# Uncomment and configure if using OpenAI API
# OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

# For development, we'll use fallback responses if no AI service is configured
# This ensures the application works even without AI services
# Enable development fallback mode for testing
ENABLE_AI_FALLBACK_MODE = True

# Import utility functions from common module to avoid duplication
from common.premium_utils import is_virtual_environment, is_development_environment

# Enable Premium dev mode only in development environments
# This flag controls whether authorized developers can access Premium features
IS_PREMIUM_DEV_MODE = is_development_environment()

# List of authorized developer usernames who can access Premium in dev mode
# This is a critical security control - only these specific users get Premium access
# All other users must go through normal payment verification
# Uses centralized configuration from config.env

# Development mode status reporting
# Provides clear feedback about the current security state
if IS_PREMIUM_DEV_MODE:
    print("WARNING: Premium dev mode is enabled - only authorized developers will have Premium access")
    print("This should only be used for development/testing purposes")
    print("Authorized developers can now test Premium features without payment")
    print(f"Environment: Virtual env={is_virtual_environment()}, Dev env={is_development_environment()}")
    print(f"Authorized users: {', '.join(AUTHORIZED_DEV_USERS)}")
else:
    print("Premium dev mode is disabled - normal payment verification required")
    print("To enable dev mode: Set DJANGO_DEVELOPMENT=true in your virtual environment")
