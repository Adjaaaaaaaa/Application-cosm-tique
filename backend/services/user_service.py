"""
User service for BeautyScan backend API.

Handles user profile retrieval and data formatting.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional

# Django imports will be handled dynamically

logger = logging.getLogger(__name__)


class UserService:
    """Service for user profile management and retrieval."""
    
    def __init__(self):
        """Initialize user service."""
        pass
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile via internal API (conforme aux exigences de formation).
        
        Cette méthode utilise l'API interne Django pour récupérer les données utilisateur
        et les injecter dans les prompts du service Premium.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile data or None if not available
        """
        return self._get_user_profile_via_internal_api(user_id)
    
    def _get_user_profile_via_internal_api(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile via internal Django API.
        
        Conforme aux exigences de formation : utiliser une API pour récupérer
        les données utilisateur et les utiliser dans les prompts IA.
        """
        try:
            import requests
            from backend.core.config import BACKEND_CONFIG
            
            # URL de l'API interne Django
            internal_api_url = f"http://127.0.0.1:8000/internal-api/user-profile/{user_id}/"
            
            # Headers avec token d'authentification interne
            headers = {
                'X-Internal-Token': 'internal_beautyscan_2024',
                'Content-Type': 'application/json'
            }
            
            # Appel à l'API interne
            logger.info(f"Récupération du profil utilisateur {user_id} via API interne")
            response = requests.get(internal_api_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and data.get("status") == "success":
                    profile_data = data.get("data")
                    logger.info(f"Profil utilisateur {user_id} récupéré avec succès via API interne")
                    return profile_data
                else:
                    logger.error(f"Erreur API interne - Réponse invalide: {data}")
            else:
                logger.error(f"Erreur API interne - Status: {response.status_code}, Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de connexion API interne: {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue API interne: {e}")
        
        # Fallback vers ORM si l'API interne échoue
        logger.warning(f"Fallback vers ORM pour le profil utilisateur {user_id}")
        return self._get_user_profile_via_orm(user_id)
    
    def _get_user_profile_via_orm(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve user profile using Django ORM (fallback)."""
        try:
            # Import Django models dynamically
            from django.contrib.auth.models import User
            from apps.accounts.models import UserProfile
            
            # Get user and profile using Django ORM
            user = User.objects.get(id=user_id)
            profile = UserProfile.objects.get(user=user)
            
            # Build profile data with all fields
            profile_data = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'skin_type': profile.skin_type,
                'age_range': profile.age_range,
                'allergies': profile.get_allergies_list() if profile.allergies else [],
                'allergies_other': profile.allergies_other,
                'skin_concerns': profile.get_skin_concerns_list() if profile.skin_concerns else [],
                'dermatological_conditions': profile.get_dermatological_conditions_list() if profile.dermatological_conditions else [],
                'dermatological_other': profile.dermatological_other,
                'product_style': profile.product_style,
                'routine_frequency': profile.routine_frequency,
                'objectives': profile.get_objectives_list() if profile.objectives else [],
                'budget': profile.budget
            }
            
            logger.info(f"Retrieved complete profile for user: {profile_data.get('username', 'unknown')}")
            logger.info(f"Profile data: {profile_data}")
            return profile_data
                
        except ImportError:
            logger.error("Django not properly configured")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user profile for user_id {user_id}: {str(e)}")
            return None

    def get_user_allergies(self, user_id: int) -> List[str]:
        """
        Get user allergies using Django ORM.
        
        Args:
            user_id: User ID
            
        Returns:
            List of allergy ingredient names
        """
        try:
            # Import Django models dynamically
            from django.contrib.auth.models import User
            from apps.accounts.models import UserProfile
            
            user = User.objects.get(id=user_id)
            profile = UserProfile.objects.get(user=user)
            
            allergies = profile.get_allergies_list() if profile.allergies else []
            if profile.allergies_other:
                allergies.append(profile.allergies_other)
                
            return allergies
                
        except ImportError:
            logger.error("Django not properly configured")
            return []
        except Exception as e:
            logger.error(f"Error retrieving allergies for user_id {user_id}: {str(e)}")
            return []
    
    def format_profile_for_ai(self, profile: Dict[str, Any]) -> str:
        """
        Format user profile for AI prompt.
        
        Args:
            profile: User profile dictionary
            
        Returns:
            Formatted profile string for AI
        """
        if not profile:
            return "Profil utilisateur non disponible"
        
        # Format allergies - MISE EN ÉVIDENCE
        allergies = profile.get("allergies", [])
        allergies_other = profile.get("allergies_other", "")
        
        if allergies or allergies_other:
            allergies_list = []
            if allergies:
                allergies_list.extend(allergies)
            if allergies_other:
                allergies_list.append(allergies_other)
            allergies_text = "🚨 " + ", ".join(allergies_list) + " 🚨"
        else:
            allergies_text = "aucune"
        
        # Format skin concerns
        skin_concerns = profile.get("skin_concerns", [])
        concerns_text = ", ".join(skin_concerns) if skin_concerns else "aucune"
        
        # Format dermatological conditions - MISE EN ÉVIDENCE
        dermatological_conditions = profile.get("dermatological_conditions", [])
        dermatological_other = profile.get("dermatological_other", "")
        
        if dermatological_conditions or dermatological_other:
            conditions_list = []
            if dermatological_conditions:
                conditions_list.extend(dermatological_conditions)
            if dermatological_other:
                conditions_list.append(dermatological_other)
            conditions_text = "⚠️ " + ", ".join(conditions_list) + " ⚠️"
        else:
            conditions_text = "aucune"
        
        # Format objectives
        objectives = profile.get("objectives", [])
        objectives_text = ", ".join(objectives) if objectives else "aucune"
        
        # Debug logging
        logger.info(f"Formatting profile for AI:")
        logger.info(f"  skin_concerns: {skin_concerns}")
        logger.info(f"  dermatological_conditions: {dermatological_conditions}")
        logger.info(f"  allergies: {allergies}")
        logger.info(f"  objectives: {objectives}")
        
        return f"""
**Profil Utilisateur:**
- **Nom:** {profile.get('username', 'utilisateur')}
- **Type de peau:** {profile.get('skin_type', 'mixte')}
- **Tranche d'âge:** {profile.get('age_range', '26-35')}
- **Allergies:** {allergies_text}
- **Préoccupations cutanées:** {concerns_text}
- **Objectifs:** {objectives_text}
- **Conditions dermatologiques:** {conditions_text}
- **Style de produits:** {profile.get('product_style', 'pharmacy')}
- **Fréquence de routine:** {profile.get('routine_frequency', 'standard')}
- **Budget:** {profile.get('budget', 'moderate')}
        """.strip()

    def _get_default_profile(self) -> Dict[str, Any]:
        """Get default profile when user profile is not available."""
        return {
            'username': 'utilisateur',
            'skin_type': 'mixte',
            'age_range': '26-35',
            'allergies': [],
            'allergies_other': '',
            'skin_concerns': [],
            'dermatological_conditions': [],
            'dermatological_other': '',
            'product_style': 'pharmacy',
            'routine_frequency': 'standard',
            'objectives': [],
            'budget': 'moderate'
        }
