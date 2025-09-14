"""
Get user allergies use case for BeautyScan application.

This use case handles retrieving user allergy information.
"""

from typing import List, Optional
from core.entities.user import User
from core.entities.profile import UserProfile
from core.exceptions import UserNotFoundError, ProfileNotFoundError
from interfaces.repositories.user_repository import UserRepository
from interfaces.repositories.profile_repository import ProfileRepository


class GetUserAllergiesUseCase:
    """
    Use case for retrieving user allergy information.
    
    This use case orchestrates the retrieval of user allergy data
    using the repository pattern.
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        profile_repository: ProfileRepository
    ):
        """
        Initialize use case with required repositories.
        
        Args:
            user_repository: Repository for user data access
            profile_repository: Repository for profile data access
        """
        self._user_repository = user_repository
        self._profile_repository = profile_repository
    
    def execute(self, user_id: int) -> List[str]:
        """
        Execute the get user allergies use case.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of allergy ingredient names
            
        Raises:
            UserNotFoundError: If user cannot be found
            ProfileNotFoundError: If profile cannot be found
        """
        # Get user entity
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        # Get user profile
        profile = self._profile_repository.get_by_user_id(user_id)
        if not profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Return all allergies including other allergies
        return profile.get_all_allergies()
    
    def execute_with_entities(self, user_id: int) -> Optional[UserProfile]:
        """
        Execute the use case and return domain entities.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserProfile entity or None if not found
        """
        # Get user entity
        user = self._user_repository.get_by_id(user_id)
        if not user:
            return None
        
        # Get user profile
        profile = self._profile_repository.get_by_user_id(user_id)
        return profile
