"""
Vues API Django pour les endpoints intégrés.
"""

import json
import sys
import os
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View

# Ajouter le chemin du backend pour importer les services
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from backend.services.enhanced_routine_service import EnhancedRoutineService
    from backend.services.ai_service import AIService
    from backend.services.user_service import UserService
    from backend.services.ingredient_service import IngredientService
except ImportError as e:
    print(f"Erreur d'import des services: {e}")
    EnhancedRoutineService = None
    AIService = None
    UserService = None
    IngredientService = None


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Endpoint de santé de l'API."""
    return JsonResponse({
        "status": "healthy",
        "message": "BeautyScan API is running",
        "version": "v1"
    })


@csrf_exempt
@require_http_methods(["POST"])
def general_question(request):
    """Endpoint pour répondre aux questions générales."""
    try:
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
        
        return JsonResponse({
            "status": "success",
            "data": response
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors du traitement: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def comprehensive_routine(request):
    """Endpoint pour générer une routine complète."""
    try:
        data = json.loads(request.body)
        
        # Créer une instance du service
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
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors de la génération: {str(e)}"
        }, status=500, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
@require_http_methods(["POST"])
def analyze_product(request):
    """Endpoint pour analyser un produit."""
    try:
        data = json.loads(request.body)
        
        # Créer une instance du service
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
        
        return JsonResponse(result, status=200, json_dumps_params={'ensure_ascii': False})
        
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Données JSON invalides"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors de l'analyse: {str(e)}"
        }, status=500, json_dumps_params={'ensure_ascii': False})


@csrf_exempt
@require_http_methods(["GET"])
def get_ingredient_info(request):
    """Endpoint pour obtenir les informations d'un ingrédient."""
    try:
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
        
        return JsonResponse(result, status=200)
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors de la récupération: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT"])
def user_profile(request):
    """Endpoint pour gérer le profil utilisateur."""
    try:
        if not UserService:
            return JsonResponse({
                "status": "error",
                "message": "Service non disponible"
            }, status=503)
        
        # Créer une instance du service
        service = UserService()
        
        if request.method == "GET":
            # Récupérer le profil depuis les paramètres GET
            user_id = request.GET.get('user_id', 1)
            result = service.get_user_profile(user_id)
        elif request.method == "POST":
            # Récupérer le profil depuis le body JSON
            data = json.loads(request.body)
            user_id = data.get('user_id', 1)
            result = service.get_user_profile(user_id)
        elif request.method == "PUT":
            # Mettre à jour le profil
            data = json.loads(request.body)
            user_id = data.get('user_id', 1)
            profile_updates = data.get('profile_updates', {})
            result = service.update_user_profile(user_id, profile_updates)
        
        return JsonResponse({
            "status": "success",
            "data": result
        }, status=200, json_dumps_params={'ensure_ascii': False})
        
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Données JSON invalides"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors de la gestion du profil: {str(e)}"
        }, status=500)
