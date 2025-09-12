"""
Production settings for BeautyScan project.

This module contains Django configuration specific to production environments.
It enforces strict security settings, uses production-grade database and email
services, and ensures that all development/testing features are disabled.

Production settings prioritize security, performance, and reliability over
development convenience. All sensitive configuration comes from environment
variables to prevent accidental exposure of secrets in code.
"""

import os
import sys
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
# Debug mode exposes sensitive information and should never be enabled
# in production environments for security reasons
DEBUG = False

# Allowed hosts for production server
# Must be explicitly set via environment variable for security
# This prevents HTTP Host header attacks
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database configuration for production
# Uses PostgreSQL Azure specifically for production (bdscanprod)
# All database credentials must be provided via environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('AZURE_DB_PROD_NAME', os.environ.get('AZURE_DB_NAME', os.environ.get('DB_NAME'))),
        'USER': os.environ.get('AZURE_DB_PROD_USER', os.environ.get('AZURE_DB_USER', os.environ.get('DB_USER'))),
        'PASSWORD': os.environ.get('AZURE_DB_PROD_PASSWORD', os.environ.get('AZURE_DB_PASSWORD', os.environ.get('DB_PASSWORD'))),
        'HOST': os.environ.get('AZURE_DB_PROD_HOST', os.environ.get('AZURE_DB_HOST', os.environ.get('DB_HOST'))),
        'PORT': os.environ.get('AZURE_DB_PROD_PORT', os.environ.get('AZURE_DB_PORT', os.environ.get('DB_PORT', '5432'))),
        'OPTIONS': {
            'sslmode': 'require',  # Required for Azure PostgreSQL
        },
    }
}

# Security settings for production
# These headers protect against common web vulnerabilities
SECURE_BROWSER_XSS_FILTER = True      # XSS protection
SECURE_CONTENT_TYPE_NOSNIFF = True    # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'              # Prevent clickjacking
SECURE_HSTS_SECONDS = 31536000        # HTTP Strict Transport Security (1 year)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True # Apply HSTS to subdomains
SECURE_HSTS_PRELOAD = True            # Allow inclusion in HSTS preload lists

# Email configuration for production
# Uses SMTP for reliable email delivery
# All email settings must be provided via environment variables
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = True                  # Use TLS for secure email transmission
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Production security: Ensure developer testing is disabled
# This is a critical security control that prevents unauthorized access
# to Premium features without payment verification
# 
# CRITICAL: This flag must NEVER be True in production
IS_PREMIUM_DEV_MODE = False

def validate_production_environment():
    """
    Validate that production environment is properly configured.
    
    This function performs runtime checks to ensure that the production
    environment is secure and properly configured. It prevents common
    misconfigurations that could lead to security vulnerabilities.
    
    Raises:
        RuntimeError: If production environment is not properly configured
    """
    # Ensure debug is disabled - critical for security
    # Debug mode exposes sensitive information and should never be enabled
    if DEBUG:
        raise RuntimeError("DEBUG must be False in production")
    
    # Ensure Premium dev mode is disabled - critical for business security
    # This prevents unauthorized access to Premium features
    if IS_PREMIUM_DEV_MODE:
        raise RuntimeError("IS_PREMIUM_DEV_MODE must be False in production")
    
    # Check for required environment variables
    # These are essential for production operation and security
    # Support Azure production-specific, Azure generic, and generic database variables
    required_vars = ['SECRET_KEY']

    # Check for database variables (priority order: Azure Prod > Azure Generic > Generic)
    db_vars_azure_prod = ['AZURE_DB_PROD_NAME', 'AZURE_DB_PROD_USER', 'AZURE_DB_PROD_PASSWORD', 'AZURE_DB_PROD_HOST']
    db_vars_azure = ['AZURE_DB_NAME', 'AZURE_DB_USER', 'AZURE_DB_PASSWORD', 'AZURE_DB_HOST']
    db_vars_generic = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']

    # Check if any of the database variable sets are present
    has_azure_prod_db = all(os.environ.get(var) for var in db_vars_azure_prod)
    has_azure_db = all(os.environ.get(var) for var in db_vars_azure)
    has_generic_db = all(os.environ.get(var) for var in db_vars_generic)

    if not (has_azure_prod_db or has_azure_db or has_generic_db):
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        missing_vars.extend([f"{var} (or Azure equivalent)" for var in db_vars_generic])
    else:
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    print("✅ Production environment validated - Premium dev mode disabled")

# Validate production environment on startup
# This ensures the application fails fast if misconfigured
# rather than running with security vulnerabilities
validate_production_environment()
