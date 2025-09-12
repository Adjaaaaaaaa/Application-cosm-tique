"""
Configuration des variables d'environnement pour BeautyScan.

Ce module centralise la gestion des variables d'environnement
et fournit des valeurs par défaut sécurisées pour le développement.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Répertoire racine du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Charger les variables d'environnement depuis le fichier .env
load_dotenv('.env')

def get_env_var(key, default=None, required=False):
    """
    Récupère une variable d'environnement avec gestion d'erreur.
    
    Args:
        key (str): Nom de la variable d'environnement
        default: Valeur par défaut si la variable n'existe pas
        required (bool): Si True, lève une exception si la variable est manquante
        
    Returns:
        str: Valeur de la variable d'environnement
        
    Raises:
        ValueError: Si la variable est requise mais manquante
    """
    value = os.environ.get(key, default)
    
    if required and value is None:
        raise ValueError(f"Variable d'environnement requise manquante: {key}")
    
    return value

# =============================================================================
# CONFIGURATION DJANGO
# =============================================================================

# Clé secrète Django (CRITIQUE pour la sécurité)
SECRET_KEY = get_env_var('SECRET_KEY', default='')

# Module de paramètres Django
DJANGO_SETTINGS_MODULE = get_env_var(
    'DJANGO_SETTINGS_MODULE',
    default='config.settings.dev'
)

# Mode debug (désactivé en production)
DEBUG = get_env_var('DEBUG', default='True').lower() == 'true'

# =============================================================================
# FLAGS DE DÉVELOPPEMENT
# =============================================================================

# Indicateurs de mode développement
DJANGO_DEVELOPMENT = get_env_var('DJANGO_DEVELOPMENT', default='True').lower() == 'true'
IS_DEVELOPMENT = get_env_var('IS_DEVELOPMENT', default='True').lower() == 'true'
LOCAL_DEVELOPMENT = get_env_var('LOCAL_DEVELOPMENT', default='True').lower() == 'true'

# =============================================================================
# CONFIGURATION BASE DE DONNÉES
# =============================================================================

# Configuration SQLite (développement)
DB_NAME = get_env_var('DB_NAME', default='db.sqlite3')
DB_USER = get_env_var('DB_USER', default='')
DB_PASSWORD = get_env_var('DB_PASSWORD', default='')
DB_HOST = get_env_var('DB_HOST', default='localhost')
DB_PORT = get_env_var('DB_PORT', default='5432')

# =============================================================================
# APIS EXTERNES
# =============================================================================

# Azure OpenAI (optionnel - pour les fonctionnalités IA)
AZURE_OPENAI_KEY = get_env_var('AZURE_OPENAI_API_KEY', default=get_env_var('OPENAI_API_KEY', default=''))
AZURE_OPENAI_ENDPOINT = get_env_var('AZURE_OPENAI_ENDPOINT', default='')

# Ollama (modèle IA local)
OLLAMA_API_URL = get_env_var('OLLAMA_API_URL', default='http://localhost:11434')

# Stripe (paiements)
STRIPE_PUBLISHABLE_KEY = get_env_var('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = get_env_var('STRIPE_SECRET_KEY', default='')

# =============================================================================
# CONFIGURATION EMAIL
# =============================================================================

# Configuration SMTP (production)
EMAIL_HOST = get_env_var('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = get_env_var('EMAIL_PORT', default='587')
EMAIL_HOST_USER = get_env_var('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = get_env_var('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = get_env_var('EMAIL_USE_TLS', default='True').lower() == 'true'

# =============================================================================
# CONFIGURATION PRODUCTION
# =============================================================================

# Hôtes autorisés pour la production
ALLOWED_HOSTS_STR = get_env_var('ALLOWED_HOSTS', default='localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]

# Utilisateurs développeurs autorisés (mode Premium dev)
AUTHORIZED_DEV_USERS_STR = get_env_var('AUTHORIZED_DEV_USERS', default='admin,testuser')
AUTHORIZED_DEV_USERS = [user.strip() for user in AUTHORIZED_DEV_USERS_STR.split(',') if user.strip()]

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def is_development_mode():
    """
    Vérifie si l'application est en mode développement.
    
    Returns:
        bool: True si en mode développement
    """
    return any([
        DJANGO_DEVELOPMENT,
        IS_DEVELOPMENT,
        LOCAL_DEVELOPMENT,
        DEBUG
    ])

def is_production_mode():
    """
    Vérifie si l'application est en mode production.
    
    Returns:
        bool: True si en mode production
    """
    return not is_development_mode()

def get_database_config():
    """
    Retourne la configuration de base de données appropriée.
    
    Returns:
        dict: Configuration de base de données
    """
    if is_development_mode():
        # SQLite pour le développement
        return {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': PROJECT_ROOT / DB_NAME,
        }
    else:
        # PostgreSQL pour la production
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }

def validate_environment():
    """
    Valide la configuration de l'environnement.
    
    Vérifie que toutes les variables requises sont présentes
    et que la configuration est cohérente.
    
    Raises:
        ValueError: Si la configuration est invalide
    """
    errors = []
    
    # Vérifications de sécurité
    if is_production_mode():
        if not SECRET_KEY:
            errors.append("SECRET_KEY doit être configurée en production")
        
        if DEBUG:
            errors.append("DEBUG doit être False en production")
    
    # Vérifications de base de données
    if is_production_mode():
        if not DB_NAME or DB_NAME == 'db.sqlite3':
            errors.append("DB_NAME doit être configuré pour la production")
        
        if not DB_USER:
            errors.append("DB_USER doit être configuré pour la production")
    
    # Vérifications d'API (optionnelles mais recommandées)
    if not AZURE_OPENAI_KEY and not OLLAMA_API_URL:
        print("⚠️  Aucune API IA configurée - certaines fonctionnalités seront limitées")
    
    if not STRIPE_SECRET_KEY:
        print("⚠️  Stripe non configuré - les paiements ne fonctionneront pas")
    
    if errors:
        raise ValueError("Erreurs de configuration:\n" + "\n".join(f"- {error}" for error in errors))

def print_environment_info():
    """
    Affiche les informations de configuration de l'environnement.
    
    Utile pour le débogage et la vérification de la configuration.
    """
    print("🔧 Configuration de l'environnement BeautyScan:")
    print(f"   Mode: {'🟢 Développement' if is_development_mode() else '🔴 Production'}")
    print(f"   Debug: {'✅ Activé' if DEBUG else '❌ Désactivé'}")
    print(f"   Base de données: {get_database_config()['ENGINE']}")
    print(f"   Utilisateurs autorisés: {', '.join(AUTHORIZED_DEV_USERS)}")
    
    if AZURE_OPENAI_KEY:
        print("   Azure OpenAI: ✅ Configuré")
    elif OLLAMA_API_URL:
        print("   Ollama: ✅ Configuré")
    else:
        print("   IA: ⚠️  Non configuré")
    
    if STRIPE_SECRET_KEY:
        print("   Stripe: ✅ Configuré")
    else:
        print("   Stripe: ⚠️  Non configuré")

# Validation automatique au chargement du module
if __name__ == "__main__":
    try:
        validate_environment()
        print_environment_info()
        print("✅ Configuration valide")
    except ValueError as e:
        print(f"❌ Configuration invalide: {e}")
        sys.exit(1)
