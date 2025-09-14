"""
API interne Django pour la récupération des profils utilisateur.
Cette API est réservée aux services internes uniquement.
"""
import json
import logging
import sys
import os
from pathlib import Path
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

# Ajouter le chemin du backend pour importer les services
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from backend.services.enhanced_routine_service import EnhancedRoutineService
    from backend.services.ai_service import AIService
    from backend.services.ingredient_service import IngredientService
except ImportError as e:
    logger.warning(f"Erreur d'import des services: {e}")
    EnhancedRoutineService = None
    AIService = None
    IngredientService = None

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

# Import Clean Architecture adapter
from .adapters.internal_api_adapter import get_user_profile_internal

# Legacy internal API - now uses Clean Architecture adapter
# The original implementation has been moved to the adapter
# while maintaining the same interface and behavior


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

@csrf_exempt
@require_http_methods(["POST"])
def comprehensive_routine_internal(request):
    """
    API interne pour générer une routine complète.
    
    Endpoint: POST /internal-api/enhanced-ai/comprehensive-routine/
    Headers requis: X-Internal-Token: internal_beautyscan_2024
    """
    try:
        # Validation de sécurité
        if not validate_internal_request(request):
            logger.warning(f"Tentative d'accès non autorisé à l'API interne depuis {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({
                'status': 'error',
                'message': 'Accès non autorisé - API interne uniquement'
            }, status=403)
        
        data = json.loads(request.body)
        
        # Créer une instance du service
        if EnhancedRoutineService is None:
            return JsonResponse({
                "status": "error",
                "message": "Service non disponible"
            }, status=503)
        
        service = EnhancedRoutineService()
        
        # Extraire les paramètres
        user_id = data.get('user_id', 1)
        routine_type = data.get('routine_type', 'evening')
        user_question = data.get('user_question', '')
        budget = data.get('budget', 50)
        product_ingredients = data.get('product_ingredients', '')
        
        # Générer la routine
        result = service.generate_routine(
            user_id=user_id,
            routine_type=routine_type,
            budget=str(budget),
            custom_question=user_question
        )
        
        logger.info(f"Routine générée avec succès pour l'utilisateur {user_id} via API interne")
        
        return JsonResponse({
            "status": "success",
            "data": result
        }, status=200, json_dumps_params={'ensure_ascii': False})
        
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Données JSON invalides"
        }, status=400, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"Erreur API interne génération routine: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors de la génération: {str(e)}"
        }, status=500, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
@require_http_methods(["POST"])
def analyze_product_internal(request):
    """
    API interne pour analyser un produit.
    
    Endpoint: POST /internal-api/ai/analyze-product/
    Headers requis: X-Internal-Token: internal_beautyscan_2024
    """
    try:
        # Validation de sécurité
        if not validate_internal_request(request):
            logger.warning(f"Tentative d'accès non autorisé à l'API interne depuis {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({
                'status': 'error',
                'message': 'Accès non autorisé - API interne uniquement'
            }, status=403)
        
        data = json.loads(request.body)
        
        # Créer une instance du service
        if AIService is None:
            return JsonResponse({
                "status": "error",
                "message": "Service non disponible"
            }, status=503)
        
        service = AIService()
        
        # Extraire les paramètres
        user_id = data.get('user_id', 1)
        product_ingredients = data.get('product_ingredients', '')
        user_question = data.get('user_question', '')
        product_info = data.get('product_info', {})
        
        # Analyser le produit
        result = service.generate_comprehensive_analysis(
            user_id=user_id,
            product_ingredients=product_ingredients,
            user_question=user_question,
            product_info=product_info
        )
        
        logger.info(f"Produit analysé avec succès pour l'utilisateur {user_id} via API interne")
        
        return JsonResponse(result, status=200, json_dumps_params={'ensure_ascii': False})
        
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Données JSON invalides"
        }, status=400)
    except Exception as e:
        logger.error(f"Erreur API interne analyse produit: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors de l'analyse: {str(e)}"
        }, status=500, json_dumps_params={'ensure_ascii': False})

@require_http_methods(["GET"])
def get_ingredient_info_internal(request):
    """
    API interne pour obtenir les informations d'un ingrédient.
    
    Endpoint: GET /internal-api/ingredients/info/
    Headers requis: X-Internal-Token: internal_beautyscan_2024
    """
    try:
        # Validation de sécurité
        if not validate_internal_request(request):
            logger.warning(f"Tentative d'accès non autorisé à l'API interne depuis {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({
                'status': 'error',
                'message': 'Accès non autorisé - API interne uniquement'
            }, status=403)
        
        ingredient_name = request.GET.get('ingredient', '')
        
        if not ingredient_name:
            return JsonResponse({
                "status": "error",
                "message": "Nom d'ingrédient requis"
            }, status=400)
        
        if not IngredientService:
            return JsonResponse({
                "status": "error",
                "message": "Service non disponible"
            }, status=503)
        
        # Créer une instance du service
        service = IngredientService()
        
        # Obtenir les informations de l'ingrédient
        result = service.get_ingredient_info(ingredient_name)
        
        logger.info(f"Informations ingrédient '{ingredient_name}' récupérées avec succès via API interne")
        
        return JsonResponse(result, status=200)
        
    except Exception as e:
        logger.error(f"Erreur API interne récupération ingrédient: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors de la récupération: {str(e)}"
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def general_question_internal(request):
    """
    API interne pour répondre aux questions générales.
    
    Endpoint: POST /internal-api/ai/general-question/
    Headers requis: X-Internal-Token: internal_beautyscan_2024
    """
    try:
        # Validation de sécurité
        if not validate_internal_request(request):
            logger.warning(f"Tentative d'accès non autorisé à l'API interne depuis {request.META.get('REMOTE_ADDR')}")
            return JsonResponse({
                'status': 'error',
                'message': 'Accès non autorisé - API interne uniquement'
            }, status=403)
        
        data = json.loads(request.body)
        
        user_id = data.get('user_id', 1)
        question = data.get('question', '')
        
        if not question:
            return JsonResponse({
                "status": "error",
                "message": "Question requise"
            }, status=400)
        
        # Créer une instance du service IA
        if AIService is None:
            return JsonResponse({
                "status": "error",
                "message": "Service IA non disponible"
            }, status=503)
        
        ai_service = AIService()
        
        # Répondre à la question générale
        response = ai_service.answer_general_question(user_id, question)
        
        logger.info(f"Question générale traitée avec succès pour l'utilisateur {user_id} via API interne")
        
        return JsonResponse({
            "status": "success",
            "data": response
        })
        
    except Exception as e:
        logger.error(f"Erreur API interne question générale: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors du traitement: {str(e)}"
        }, status=500)
