"""
UserService adapter for Clean Architecture compatibility.

This adapter maintains backward compatibility with the existing UserService
while using the new domain entities and value objects.
"""

import logging
from typing import Dict, Any, List, Optional

from core.entities.user import User
from core.entities.profile import UserProfile
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.exceptions import UserNotFoundError, ProfileNotFoundError

logger = logging.getLogger(__name__)


class UserServiceAdapter:
    """
    Adapter for UserService to maintain backward compatibility.
    
    This class provides the same interface as the original UserService
    but uses the new domain entities internally.
    """
    
    def __init__(self):
        """Initialize user service adapter."""
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
            from backend.core.config import settings
            
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
            from django.contrib.auth.models import User as DjangoUser
            from apps.accounts.models import UserProfile as DjangoUserProfile
            
            # Get user and profile using Django ORM
            django_user = DjangoUser.objects.get(id=user_id)
            django_profile = DjangoUserProfile.objects.get(user=django_user)
            
            # Convert to domain entities
            user = User(
                user_id=django_user.id,
                username=django_user.username,
                email=django_user.email,
                first_name=django_user.first_name,
                last_name=django_user.last_name,
                is_active=django_user.is_active
            )
            
            profile = UserProfile(
                user=user,
                skin_type=SkinType.from_string(django_profile.skin_type),
                age_range=AgeRange.from_string(django_profile.age_range),
                skin_concerns=django_profile.get_skin_concerns_list(),
                dermatological_conditions=django_profile.get_dermatological_conditions_list(),
                dermatological_other=django_profile.dermatological_other,
                allergies=django_profile.get_allergies_list(),
                allergies_other=django_profile.allergies_other,
                product_style=django_profile.product_style,
                routine_frequency=django_profile.routine_frequency,
                objectives=django_profile.get_objectives_list(),
                budget=django_profile.budget,
                subscription_type=django_profile.subscription_type
            )
            
            # Convert to dictionary format expected by existing code
            profile_data = profile.to_dict()
            
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
            from django.contrib.auth.models import User as DjangoUser
            from apps.accounts.models import UserProfile as DjangoUserProfile
            
            django_user = DjangoUser.objects.get(id=user_id)
            django_profile = DjangoUserProfile.objects.get(user=django_user)
            
            # Convert to domain entities
            user = User(
                user_id=django_user.id,
                username=django_user.username,
                email=django_user.email,
                first_name=django_user.first_name,
                last_name=django_user.last_name,
                is_active=django_user.is_active
            )
            
            profile = UserProfile(
                user=user,
                skin_type=SkinType.from_string(django_profile.skin_type),
                age_range=AgeRange.from_string(django_profile.age_range),
                skin_concerns=django_profile.get_skin_concerns_list(),
                dermatological_conditions=django_profile.get_dermatological_conditions_list(),
                dermatological_other=django_profile.dermatological_other,
                allergies=django_profile.get_allergies_list(),
                allergies_other=django_profile.allergies_other,
                product_style=django_profile.product_style,
                routine_frequency=django_profile.routine_frequency,
                objectives=django_profile.get_objectives_list(),
                budget=django_profile.budget,
                subscription_type=django_profile.subscription_type
            )
            
            allergies = profile.get_all_allergies()
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
        
        # Convert dictionary to domain entities for formatting
        try:
            user = User(
                user_id=profile.get('user_id', 0),
                username=profile.get('username', 'utilisateur'),
                email=profile.get('email', ''),
                first_name=profile.get('first_name', ''),
                last_name=profile.get('last_name', ''),
                is_active=True
            )
            
            domain_profile = UserProfile(
                user=user,
                skin_type=SkinType.from_string(profile.get('skin_type', '')),
                age_range=AgeRange.from_string(profile.get('age_range', '')),
                skin_concerns=profile.get('skin_concerns', []),
                dermatological_conditions=profile.get('dermatological_conditions', []),
                dermatological_other=profile.get('dermatological_other', ''),
                allergies=profile.get('allergies', []),
                allergies_other=profile.get('allergies_other', ''),
                product_style=profile.get('product_style', ''),
                routine_frequency=profile.get('routine_frequency', ''),
                objectives=profile.get('objectives', []),
                budget=profile.get('budget', ''),
                subscription_type=profile.get('subscription_type', 'free')
            )
            
            # Use domain entity formatting
            formatted = domain_profile.format_for_ai()
            
            # Debug logging
            logger.info(f"Formatting profile for AI:")
            logger.info(f"  skin_concerns: {domain_profile.skin_concerns}")
            logger.info(f"  dermatological_conditions: {domain_profile.dermatological_conditions}")
            logger.info(f"  allergies: {domain_profile.allergies}")
            logger.info(f"  objectives: {domain_profile.objectives}")
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting profile for AI: {str(e)}")
            return "Erreur lors du formatage du profil pour l'IA"

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
