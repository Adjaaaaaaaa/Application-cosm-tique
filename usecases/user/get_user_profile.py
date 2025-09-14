"""
Get user profile use case for BeautyScan application.

This use case handles retrieving user profile information
using the repository pattern.
"""

from typing import Optional, Dict, Any
from core.entities.user import User
from core.entities.profile import UserProfile
from core.exceptions import UserNotFoundError, ProfileNotFoundError
from interfaces.repositories.user_repository import UserRepository
from interfaces.repositories.profile_repository import ProfileRepository


class GetUserProfileUseCase:
    """
    Use case for retrieving user profile information.
    
    This use case orchestrates the retrieval of user and profile data
    using the repository pattern, ensuring separation of concerns.
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
    
    def execute(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Execute the get user profile use case.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary containing user profile data or None if not found
            
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
        
        # Convert to dictionary format for backward compatibility
        return profile.to_dict()
    
    def execute_with_user_entity(self, user_id: int) -> Optional[UserProfile]:
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
