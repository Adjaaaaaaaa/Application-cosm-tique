"""
Views for AI Routines app - Enhanced with Azure GPT-4, OpenFact Beauty, and PubChem
"""

import json
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

# Configuration du backend API - PORT 8000
API_BASE_URL = "http://127.0.0.1:8000/api/v1"


@login_required
def ai_routines_view(request):
    """Vue principale pour les routines IA."""
    return render(request, 'ai_routines/ai_routines.html')


@login_required
def beauty_assistant_view(request):
    """Vue pour l'assistant beauté avec services intégrés."""
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            routine_type = request.POST.get('routine_type', 'evening')
            question = request.POST.get('question', '')
            budget = int(request.POST.get('budget', 50))
            product_ingredients = request.POST.get('product_ingredients', '')
            
            # Appeler l'API
            api_url = f"{API_BASE_URL}/enhanced-ai/comprehensive-routine"
            
            payload = {
                "user_id": request.user.id,
                "routine_type": routine_type,
                "user_question": question,
                "budget": budget
            }
            
            if product_ingredients:
                payload["product_ingredients"] = product_ingredients
            
            # Faire l'appel à l'API
            response = requests.post(
                api_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                api_data = response.json()
                return JsonResponse({
                    "status": "success",
                    "data": api_data
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"Erreur API: {response.status_code} - {response.text}"
                }, status=500)
                
        except requests.exceptions.ConnectionError:
            return JsonResponse({
                "status": "error",
                "message": "Erreur de connexion au serveur."
            }, status=503)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Erreur lors de la génération: {str(e)}"
            }, status=500)
    
    return render(request, 'ai_routines/beauty_assistant.html')


@login_required
def product_analysis_view(request):
    """Vue pour l'analyse de produits avec services intégrés."""
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            product_ingredients = request.POST.get('product_ingredients', '')
            user_question = request.POST.get('user_question', '')
            product_name = request.POST.get('product_name', '')
            product_brand = request.POST.get('product_brand', '')
            
            # Appeler l'API pour l'analyse de produits
            api_url = f"{API_BASE_URL}/ai/analyze-product"
            
            payload = {
                "user_id": request.user.id,
                "product_ingredients": product_ingredients,
                "user_question": user_question,
                "product_info": {
                    "name": product_name,
                    "brand": product_brand
                }
            }
            
            # Faire l'appel à l'API
            response = requests.post(
                api_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                api_data = response.json()
                return JsonResponse({
                    "status": "success",
                    "data": api_data
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"Erreur API: {response.status_code} - {response.text}"
                }, status=500)
                
        except requests.exceptions.ConnectionError:
            return JsonResponse({
                "status": "error",
                "message": "Erreur de connexion au serveur."
            }, status=503)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Erreur lors de l'analyse: {str(e)}"
            }, status=500)
    
    return render(request, 'ai_routines/product_analysis.html')


@login_required
def routine_history_view(request):
    """Vue pour l'historique des routines."""
    try:
        # Appeler l'API pour récupérer l'historique
        api_url = f"{API_BASE_URL}/routines/history"
        
        response = requests.get(
            api_url,
            params={"user_id": request.user.id},
            timeout=10
        )
        
        if response.status_code == 200:
            routines = response.json()
        else:
            routines = []
            
    except Exception:
        routines = []
    
    return render(request, 'ai_routines/routine_history.html', {
        'routines': routines
    })


@login_required
def routine_detail_view(request, routine_id):
    """Vue pour le détail d'une routine."""
    try:
        # Appeler l'API pour récupérer le détail
        api_url = f"{API_BASE_URL}/routines/{routine_id}"
        
        response = requests.get(
            api_url,
            params={"user_id": request.user.id},
            timeout=10
        )
        
        if response.status_code == 200:
            routine = response.json()
        else:
            routine = None
            
    except Exception:
        routine = None
    
    if not routine:
        messages.error(request, "Routine non trouvée.")
        return redirect('ai_routines:routine_history')
    
    return render(request, 'ai_routines/routine_detail.html', {
        'routine': routine
    })


@login_required
def user_profile_view(request):
    """Vue pour le profil utilisateur."""
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            profile_data = {
                "age": int(request.POST.get('age', 25)),
                "skin_type": request.POST.get('skin_type', 'normal'),
                "skin_concerns": request.POST.getlist('skin_concerns'),
                "allergies": request.POST.getlist('allergies'),
                "budget_range": request.POST.get('budget_range', 'medium'),
                "routine_complexity": request.POST.get('routine_complexity', 'moderate')
            }
            
            # Appeler l'API pour mettre à jour le profil
            api_url = f"{API_BASE_URL}/user/profile"
            
            response = requests.put(
                api_url,
                json={
                    "user_id": request.user.id,
                    "profile_updates": profile_data
                },
                timeout=10
            )
            
            if response.status_code == 200:
                messages.success(request, "Profil mis à jour avec succès !")
            else:
                messages.error(request, "Erreur lors de la mise à jour du profil.")
                
        except Exception as e:
            messages.error(request, f"Erreur: {str(e)}")
    
    # Récupérer le profil actuel
    try:
        api_url = f"{API_BASE_URL}/user/profile"
        
        response = requests.get(
            api_url,
            params={"user_id": request.user.id},
            timeout=10
        )
        
        if response.status_code == 200:
            profile = response.json()
        else:
            profile = None
            
    except Exception:
        profile = None
    
    return render(request, 'ai_routines/user_profile.html', {
        'profile': profile
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_beauty_assistant(request):
    """API endpoint pour l'assistant beauté."""
    try:
        data = json.loads(request.body)
        
        routine_type = data.get('routine_type', 'général')
        question = data.get('question', '')
        budget = data.get('budget', 50)
        user_id = request.user.id if request.user.is_authenticated else 1
        
        # Déterminer le type de question
        if routine_type == 'général' or not any(keyword in question.lower() for keyword in ['routine', 'fais-moi', 'crée', 'génère']):
            # Question générale - utiliser directement le service IA
            try:
                from backend.services.ai_service import AIService
                ai_service = AIService()
                response = ai_service.answer_general_question(user_id, question)
                return JsonResponse({
                    "status": "success",
                    "data": response
                })
            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "message": f"Erreur service IA: {str(e)}"
                }, status=500)
        else:
            # Demande de routine - utiliser l'endpoint des routines
            api_url = f"{API_BASE_URL}/enhanced-ai/comprehensive-routine"
            payload = {
                "user_id": user_id,
                "routine_type": routine_type,
                "user_question": question,
                "budget": budget
            }
            
            # Faire l'appel à l'API
            response = requests.post(
                api_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                api_data = response.json()
                return JsonResponse({
                    "status": "success",
                    "data": api_data
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"Erreur API: {response.status_code} - {response.text}"
                }, status=500)
            
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            "status": "error",
            "message": "Erreur de connexion au serveur."
        }, status=503)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Erreur lors de la génération: {str(e)}"
        }, status=500)
