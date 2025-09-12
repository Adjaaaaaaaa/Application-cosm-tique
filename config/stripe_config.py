"""
Configuration Stripe pour BeautyScan Premium.

Ce module gère la configuration et les utilitaires Stripe
pour les paiements Premium de l'application.
"""

import os
import stripe
from django.conf import settings

# Configuration des produits et prix
STRIPE_PRODUCTS = {
    'premium': {
        'name': 'Abonnement Premium BeautyScan',
        'description': 'Accès complet aux fonctionnalités IA avancées',
        'price': 999,  # 9.99 EUR en centimes
        'currency': 'eur',
        'interval': 'month',  # Abonnement mensuel
    }
}

# Événements webhook à surveiller
STRIPE_WEBHOOK_EVENTS = [
    'checkout.session.completed',
    'payment_intent.succeeded',
    'payment_intent.payment_failed',
    'customer.subscription.created',
    'customer.subscription.updated',
    'customer.subscription.deleted',
]

def get_ngrok_url():
    """
    Récupère l'URL ngrok depuis l'environnement ou génère une URL par défaut.
    
    Returns:
        str: URL ngrok ou localhost par défaut
    """
    # Vérifier si ngrok est configuré dans l'environnement
    ngrok_url = os.environ.get('NGROK_URL')
    
    if ngrok_url:
        return ngrok_url.rstrip('/')
    
    # Fallback vers localhost
    return 'http://localhost:8000'

def get_stripe_redirect_urls():
    """
    Génère les URLs de redirection Stripe dynamiquement.
    
    Returns:
        dict: URLs de redirection avec support ngrok
    """
    base_url = get_ngrok_url()
    
    return {
        'success': f'{base_url}/payments/stripe-success/',
        'cancel': f'{base_url}/payments/upgrade/',
        'webhook': f'{base_url}/payments/stripe-webhook/',
    }

# URLs de redirection dynamiques
STRIPE_REDIRECT_URLS = get_stripe_redirect_urls()

def is_stripe_configured():
    """
    Vérifie si Stripe est correctement configuré.
    
    Returns:
        bool: True si Stripe est configuré, False sinon
    """
    required_keys = [
        'STRIPE_PUBLISHABLE_KEY',
        'STRIPE_SECRET_KEY',
    ]
    
    for key in required_keys:
        if not getattr(settings, key, None):
            return False
    
    return True

def get_premium_product_config():
    """
    Récupère la configuration du produit Premium.
    
    Returns:
        dict: Configuration du produit Premium
    """
    return STRIPE_PRODUCTS.get('premium', {})

def get_stripe_api_key():
    """
    Récupère la clé API Stripe.
    
    Returns:
        str: Clé API Stripe ou None si non configurée
    """
    return getattr(settings, 'STRIPE_SECRET_KEY', None)

def get_stripe_publishable_key():
    """
    Récupère la clé publique Stripe.
    
    Returns:
        str: Clé publique Stripe ou None si non configurée
    """
    return getattr(settings, 'STRIPE_PUBLISHABLE_KEY', None)

def get_stripe_webhook_secret():
    """
    Récupère le secret webhook Stripe.
    
    Returns:
        str: Secret webhook Stripe ou None si non configurée
    """
    return getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

def get_webhook_url_for_stripe():
    """
    Génère l'URL webhook à configurer dans le dashboard Stripe.
    
    Returns:
        str: URL webhook complète pour Stripe
    """
    base_url = get_ngrok_url()
    return f'{base_url}/payments/stripe-webhook/'

def validate_stripe_webhook(payload, sig_header, webhook_secret):
    """
    Valide la signature d'un webhook Stripe.
    
    Args:
        payload: Corps de la requête webhook
        sig_header: En-tête de signature Stripe
        webhook_secret: Secret webhook pour validation
        
    Returns:
        dict: Événement Stripe validé ou None si invalide
    """
    try:
        if not webhook_secret:
            return None
            
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        return event
    except ValueError:
        # Payload invalide
        return None
    except stripe.error.SignatureVerificationError:
        # Signature invalide
        return None
    except Exception:
        # Autre erreur
        return None

def create_premium_checkout_session(user, success_url=None, cancel_url=None):
    """
    Crée une session de checkout Stripe pour l'upgrade Premium.
    
    OPTION 1 (SANS WEBHOOK): Utilise uniquement la redirection directe vers /payments/stripe-success/
    Cette option active Premium immédiatement après le paiement via la page de succès.
    
    Args:
        user: Utilisateur Django
        success_url: URL de succès (optionnelle, utilise l'URL par défaut si None)
        cancel_url: URL d'annulation (optionnelle, utilise l'URL par défaut si None)
        
    Returns:
        dict: Session de checkout créée ou None si erreur
    """
    try:
        if not is_stripe_configured():
            return None
            
        stripe.api_key = get_stripe_api_key()
        premium_config = get_premium_product_config()
        
        # OPTION 1: URLs de redirection directe (sans webhook)
        # Utiliser les URLs par défaut si non spécifiées
        if success_url is None:
            success_url = STRIPE_REDIRECT_URLS['success']
        if cancel_url is None:
            cancel_url = STRIPE_REDIRECT_URLS['cancel']
        
        # Créer la session de checkout avec redirection directe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': premium_config.get('currency', 'eur'),
                    'product_data': {
                        'name': premium_config.get('name', 'Abonnement Premium BeautyScan'),
                        'description': premium_config.get('description', 'Accès complet aux fonctionnalités IA avancées'),
                        'images': ['https://via.placeholder.com/150x150?text=BeautyScan'],
                    },
                    'unit_amount': premium_config.get('price', 999),  # 9.99 EUR en centimes
                },
                'quantity': 1,
            }],
            mode='payment',  # Paiement unique (pas d'abonnement récurrent)
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',  # Ajouter l'ID de session
            cancel_url=cancel_url,
            metadata={
                'user_id': user.id,
                'subscription_type': 'premium',
                'product_name': premium_config.get('name', 'Premium'),
                'payment_method': 'stripe_direct',  # Indiquer que c'est l'option 1
            },
            customer_email=user.email,
            allow_promotion_codes=True,
            billing_address_collection='required',
            locale='fr',
        )
        
        return checkout_session
        
    except Exception as e:
        print(f"Erreur lors de la création de la session Stripe: {e}")
        return None

def print_stripe_config_info():
    """
    Affiche les informations de configuration Stripe pour l'équipe.
    
    Utile pour configurer le dashboard Stripe et partager les informations.
    """
    print("🔧 Configuration Stripe BeautyScan:")
    print(f"   Base URL: {get_ngrok_url()}")
    print(f"   Webhook URL: {get_webhook_url_for_stripe()}")
    print(f"   Success URL: {STRIPE_REDIRECT_URLS['success']}")
    print(f"   Cancel URL: {STRIPE_REDIRECT_URLS['cancel']}")
    
    if is_stripe_configured():
        print("   ✅ Clés Stripe configurées")
        print("   📋 Instructions pour l'équipe:")
        print("      1. Configurer le webhook dans Stripe avec l'URL ci-dessus")
        print("      2. Ajouter NGROK_URL=votre_url_ngrok dans .env")
        print("      3. Tester avec les cartes de test Stripe")
    else:
        print("   ❌ Clés Stripe manquantes")
        print("   📋 Vérifier STRIPE_PUBLISHABLE_KEY et STRIPE_SECRET_KEY dans .env")

def disable_webhooks_for_option1():
    """
    Désactive les webhooks pour forcer l'utilisation de l'option 1 (sans webhook).
    
    Cette fonction modifie la configuration pour utiliser uniquement la redirection directe
    vers /payments/stripe-success/ sans dépendre des webhooks Stripe.
    
    Returns:
        dict: Configuration modifiée pour l'option 1
    """
    print("🔧 Configuration OPTION 1 (SANS WEBHOOK) activée")
    print("   ✅ Webhooks désactivés")
    print("   ✅ Redirection directe vers /payments/stripe-success/")
    print("   ✅ Activation Premium immédiate après paiement")
    
    # Modifier la configuration pour l'option 1
    global STRIPE_WEBHOOK_EVENTS
    STRIPE_WEBHOOK_EVENTS = []  # Aucun événement webhook
    
    return {
        'webhooks_disabled': True,
        'option': 'option1_no_webhook',
        'success_url': STRIPE_REDIRECT_URLS['success'],
        'cancel_url': STRIPE_REDIRECT_URLS['cancel'],
        'description': 'Premium activé immédiatement via redirection directe'
    }
