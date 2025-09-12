"""
API interne Django pour la récupération des profils utilisateur.
Cette API est réservée aux services internes uniquement.
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from apps.accounts.models import UserProfile
from backend.core.exceptions import BeautyScanException

logger = logging.getLogger(__name__)

def validate_internal_request(request):
    """
    Valide que la requête provient d'un service interne.
    Vérifie l'IP et/ou un token d'authentification interne.
    """
    # Vérifier l'IP (localhost uniquement)
    client_ip = request.META.get('REMOTE_ADDR')
    if client_ip not in ['127.0.0.1', 'localhost']:
        return False
    
    # Vérifier un header d'authentification interne (optionnel)
    internal_token = request.META.get('HTTP_X_INTERNAL_TOKEN')
    expected_token = getattr(settings, 'INTERNAL_API_TOKEN', 'internal_beautyscan_2024')
    
    if internal_token != expected_token:
        return False
    
    return True

@require_http_methods(["GET"])
@never_cache
def get_user_profile_internal(request, user_id):
    """
    API interne pour récupérer le profil utilisateur complet.
    
    Endpoint: GET /internal-api/user-profile/<user_id>/
    Headers requis: X-Internal-Token: internal_beautyscan_2024
    
    Cette API est réservée aux services internes uniquement.
    """
    try:
        # Validation de sécurité
        if not validate_internal_request(request):
            logger.warning(f"Tentative d'accès non autorisé à l'API interne depuis {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({
                'status': 'error',
                'message': 'Accès non autorisé - API interne uniquement'
            }, status=403)
        
        # Récupération du profil via ORM Django
        try:
            user = User.objects.get(id=user_id)
            profile = UserProfile.objects.get(user=user)
        except User.DoesNotExist:
            logger.warning(f"Utilisateur {user_id} non trouvé")
            return JsonResponse({
                'status': 'error',
                'message': f'Utilisateur {user_id} non trouvé'
            }, status=404)
        except UserProfile.DoesNotExist:
            logger.warning(f"Profil utilisateur {user_id} non trouvé")
            return JsonResponse({
                'status': 'error',
                'message': f'Profil utilisateur {user_id} non trouvé'
            }, status=404)
        
        # Construction de la réponse avec TOUTES les données du profil
        profile_data = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'is_active': user.is_active,
            
            # Données du profil utilisateur
            'skin_type': profile.skin_type,
            'age_range': profile.age_range,
            'budget': profile.budget,
            'product_style': profile.product_style,
            'routine_frequency': profile.routine_frequency,
            
            # Listes JSON - s'assurer que les méthodes existent et gérer les erreurs d'encodage
            'skin_concerns': profile.get_skin_concerns_list() if hasattr(profile, 'get_skin_concerns_list') else [],
            'allergies': profile.get_allergies_list() if hasattr(profile, 'get_allergies_list') else [],
            'dermatological_conditions': profile.get_dermatological_conditions_list() if hasattr(profile, 'get_dermatological_conditions_list') else [],
            'objectives': profile.get_objectives_list() if hasattr(profile, 'get_objectives_list') else [],
            
            # Données de souscription
            'subscription_type': profile.subscription_type,
            
            # Métadonnées
            'profile_created': profile.created_at.isoformat() if profile.created_at else None,
            'profile_updated': profile.updated_at.isoformat() if profile.updated_at else None,
        }
        
        logger.info(f"Profil utilisateur {user_id} récupéré avec succès via API interne")
        
        return JsonResponse({
            'status': 'success',
            'data': profile_data,
            'timestamp': {'retrieved_at': profile.updated_at.isoformat() if profile.updated_at else None}
        })
        
    except Exception as e:
        logger.error(f"Erreur API interne profil utilisateur {user_id}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'message': f'Erreur interne du serveur: {str(e)}',
            'error_code': 'INTERNAL_ERROR'
        }, status=500)

@require_http_methods(["GET"])
@never_cache
def health_check_internal(request):
    """
    Health check pour l'API interne.
    
    Endpoint: GET /internal-api/health/
    """
    try:
        # Test de base de données
        user_count = User.objects.count()
        profile_count = UserProfile.objects.count()
        
        return JsonResponse({
            'status': 'success',
            'service': 'internal-api',
            'version': '1.0.0',
            'database': {
                'connected': True,
                'users_count': user_count,
                'profiles_count': profile_count
            },
            'timestamp': {'checked_at': 'now'}
        })
        
    except Exception as e:
        logger.error(f"Health check API interne échoué: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'service': 'internal-api',
            'message': 'Service indisponible',
            'error': str(e)
        }, status=500)
