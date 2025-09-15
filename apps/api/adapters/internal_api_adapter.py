"""
Internal API adapter for Clean Architecture.

This adapter transforms the internal API endpoints to use Clean Architecture
use cases while maintaining the same interface and behavior.
"""

import logging
from typing import Dict, Any, Optional
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from usecases.user.get_user_profile import GetUserProfileUseCase
from usecases.user.update_user_profile import UpdateUserProfileUseCase
from infrastructure.repositories.django_user_repository import DjangoUserRepository
from infrastructure.repositories.django_profile_repository import DjangoProfileRepository
from core.exceptions import UserNotFoundError, ProfileNotFoundError

logger = logging.getLogger(__name__)


class InternalAPIAdapter:
    """
    Adapter for internal API using Clean Architecture.
    
    This adapter handles internal API requests using use cases
    while maintaining the same interface as the original API.
    """
    
    def __init__(self):
        """Initialize adapter with repositories and use cases."""
        # Create repositories
        self._user_repository = DjangoUserRepository()
        self._profile_repository = DjangoProfileRepository()
        
        # Create use cases
        self._get_user_profile_use_case = GetUserProfileUseCase(
            self._user_repository,
            self._profile_repository
        )
        self._update_user_profile_use_case = UpdateUserProfileUseCase(
            self._user_repository,
            self._profile_repository
        )
    
    def handle_get_user_profile(self, request: HttpRequest, user_id: int) -> JsonResponse:
        """
        Handle get user profile API request using Clean Architecture.
        
        Args:
            request: Django HTTP request
            user_id: User identifier
            
        Returns:
            JSON response with user profile data
        """
        try:
            # Validate internal request
            if not self._validate_internal_request(request):
                logger.warning(f"Unauthorized access attempt to internal API from {request.META.get('REMOTE_ADDR')}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Accès non autorisé - API interne uniquement'
                }, status=403)
            
            # Get user profile using use case
            profile_data = self._get_user_profile_use_case.execute(user_id)
            
            if not profile_data:
                logger.warning(f"User profile {user_id} not found")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Profil utilisateur {user_id} non trouvé'
                }, status=404)
            
            # Return success response
            return JsonResponse({
                'status': 'success',
                'data': profile_data
            })
            
        except UserNotFoundError:
            logger.warning(f"User {user_id} not found")
            return JsonResponse({
                'status': 'error',
                'message': f'Utilisateur {user_id} non trouvé'
            }, status=404)
        except ProfileNotFoundError:
            logger.warning(f"User profile {user_id} not found")
            return JsonResponse({
                'status': 'error',
                'message': f'Profil utilisateur {user_id} non trouvé'
            }, status=404)
        except Exception as e:
            logger.error(f"Unexpected error in internal API: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Erreur interne du serveur'
            }, status=500)
    
    def handle_update_user_profile(self, request: HttpRequest) -> JsonResponse:
        """
        Handle update user profile API request using Clean Architecture.
        
        Args:
            request: Django HTTP request with JSON body containing user_id and profile_updates
            
        Returns:
            JSON response with update result
        """
        try:
            # Validate internal request
            if not self._validate_internal_request(request):
                logger.warning(f"Unauthorized access attempt to internal API from {request.META.get('REMOTE_ADDR')}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Accès non autorisé - API interne uniquement'
                }, status=403)
            
            # Parse JSON data
            import json
            data = json.loads(request.body)
            user_id = data.get('user_id')
            profile_updates = data.get('profile_updates', {})
            
            if not user_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'user_id est requis'
                }, status=400)
            
            # Update user profile using use case
            updated_profile = self._update_user_profile_use_case.execute(user_id, profile_updates)
            
            if updated_profile:
                logger.info(f"User profile {user_id} updated successfully")
                return JsonResponse({
                    'status': 'success',
                    'message': 'Profil mis à jour avec succès',
                    'data': {
                        'user_id': user_id,
                        'updated_at': 'now'
                    }
                })
            else:
                logger.warning(f"Failed to update user profile {user_id}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Échec de la mise à jour du profil'
                }, status=500)
            
        except UserNotFoundError:
            logger.warning(f"User {user_id} not found for update")
            return JsonResponse({
                'status': 'error',
                'message': f'Utilisateur {user_id} non trouvé'
            }, status=404)
        except ProfileNotFoundError:
            logger.warning(f"User profile {user_id} not found for update")
            return JsonResponse({
                'status': 'error',
                'message': f'Profil utilisateur {user_id} non trouvé'
            }, status=404)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in update profile request")
            return JsonResponse({
                'status': 'error',
                'message': 'Format JSON invalide'
            }, status=400)
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Erreur interne du serveur',
                'error': str(e)
            }, status=500)
    
    def _validate_internal_request(self, request: HttpRequest) -> bool:
        """
        Validate that the request is from an internal service.
        
        Args:
            request: Django HTTP request
            
        Returns:
            True if request is valid, False otherwise
        """
        # Check for internal token
        internal_token = request.META.get('HTTP_X_INTERNAL_TOKEN')
        if not internal_token:
            return False
        
        # Validate token
        expected_token = 'internal_beautyscan_2024'
        if internal_token != expected_token:
            return False
        
        return True


# Create global adapter instance
internal_api_adapter = InternalAPIAdapter()


@require_http_methods(["GET"])
@never_cache
def get_user_profile_internal(request: HttpRequest, user_id: int) -> JsonResponse:
    """
    Internal API endpoint for getting user profile using Clean Architecture.
    
    This endpoint maintains the same interface as the original
    while using Clean Architecture internally.
    
    Endpoint: GET /internal-api/user-profile/<user_id>/
    Headers required: X-Internal-Token: internal_beautyscan_2024
    """
    return internal_api_adapter.handle_get_user_profile(request, user_id)


@csrf_exempt
@require_http_methods(["PUT"])
def update_user_profile_internal(request: HttpRequest) -> JsonResponse:
    """
    Internal API endpoint for updating user profile using Clean Architecture.
    
    Endpoint: PUT /internal-api/user/profile
    Headers required: X-Internal-Token: internal_beautyscan_2024
    Body: {"user_id": int, "profile_updates": {...}}
    """
    return internal_api_adapter.handle_update_user_profile(request)
