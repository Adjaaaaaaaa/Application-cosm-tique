"""
Infrastructure adapter for UserService using Clean Architecture.

This adapter wires up the use cases with concrete Django repositories
and provides the same interface as the original UserService.
"""

import logging
from typing import Dict, Any, List, Optional

from usecases.user.get_user_profile import GetUserProfileUseCase
from usecases.user.get_user_allergies import GetUserAllergiesUseCase
from usecases.user.format_profile_for_ai import FormatProfileForAIUseCase

from infrastructure.repositories.django_user_repository import DjangoUserRepository
from infrastructure.repositories.django_profile_repository import DjangoProfileRepository

logger = logging.getLogger(__name__)


class UserServiceInfrastructureAdapter:
    """
    Infrastructure adapter for UserService using Clean Architecture.
    
    This adapter wires up the use cases with concrete Django repositories
    and provides the same interface as the original UserService.
    """
    
    def __init__(self):
        """Initialize adapter with concrete repositories and use cases."""
        # Create concrete repositories
        self._user_repository = DjangoUserRepository()
        self._profile_repository = DjangoProfileRepository()
        
        # Create use cases with repositories
        self._get_user_profile_use_case = GetUserProfileUseCase(
            self._user_repository,
            self._profile_repository
        )
        
        self._get_user_allergies_use_case = GetUserAllergiesUseCase(
            self._user_repository,
            self._profile_repository
        )
        
        self._format_profile_for_ai_use_case = FormatProfileForAIUseCase()
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile using Clean Architecture with Django repositories.
        
        Args:
            user_id: User ID
            
        Returns:
            User profile data or None if not available
        """
        try:
            return self._get_user_profile_use_case.execute(user_id)
        except Exception as e:
            logger.error(f"Error getting user profile for user_id {user_id}: {str(e)}")
            return None
    
    def get_user_allergies(self, user_id: int) -> List[str]:
        """
        Get user allergies using Clean Architecture with Django repositories.
        
        Args:
            user_id: User ID
            
        Returns:
            List of allergy ingredient names
        """
        try:
            return self._get_user_allergies_use_case.execute(user_id)
        except Exception as e:
            logger.error(f"Error getting user allergies for user_id {user_id}: {str(e)}")
            return []
    
    def format_profile_for_ai(self, profile: Dict[str, Any]) -> str:
        """
        Format user profile for AI prompt using Clean Architecture.
        
        Args:
            profile: User profile dictionary
            
        Returns:
            Formatted profile string for AI
        """
        try:
            return self._format_profile_for_ai_use_case.execute(profile)
        except Exception as e:
            logger.error(f"Error formatting profile for AI: {str(e)}")
            return "Erreur lors du formatage du profil pour l'IA"
