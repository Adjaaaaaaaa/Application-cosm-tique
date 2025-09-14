"""
Update user profile use case for BeautyScan application.

This use case handles updating user profile information
using the repository pattern.
"""

from typing import Dict, Any, Optional
from core.entities.user import User
from core.entities.profile import UserProfile
from core.exceptions import UserNotFoundError, ProfileNotFoundError, InvalidInputException
from interfaces.repositories.user_repository import UserRepository
from interfaces.repositories.profile_repository import ProfileRepository


class UpdateUserProfileUseCase:
    """
    Use case for updating user profile information.
    
    This use case orchestrates the update of user and profile data
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
    
    def execute(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[UserProfile]:
        """
        Execute the update user profile use case.
        
        Args:
            user_id: User identifier
            profile_data: Dictionary containing profile updates
            
        Returns:
            Updated UserProfile entity or None if update failed
            
        Raises:
            UserNotFoundError: If user cannot be found
            ProfileNotFoundError: If profile cannot be found
            InvalidInputException: If profile data is invalid
        """
        # Get user entity
        user = self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        # Get current profile
        current_profile = self._profile_repository.get_by_user_id(user_id)
        if not current_profile:
            raise ProfileNotFoundError(f"Profile for user {user_id} not found")
        
        # Validate and update user data
        self._update_user_data(user, profile_data)
        
        # Validate and update profile data
        self._update_profile_data(current_profile, profile_data)
        
        # Save updated entities
        updated_user = self._user_repository.save(user)
        updated_profile = self._profile_repository.save(current_profile)
        
        return updated_profile
    
    def _update_user_data(self, user: User, profile_data: Dict[str, Any]) -> None:
        """
        Update user entity with form data.
        
        Args:
            user: User entity to update
            profile_data: Form data containing user updates
        """
        # Update user fields if provided
        if 'first_name' in profile_data:
            user._first_name = profile_data['first_name'].strip()
        
        if 'last_name' in profile_data:
            user._last_name = profile_data['last_name'].strip()
        
        if 'email' in profile_data:
            email = profile_data['email'].strip()
            if email and '@' in email:  # Basic email validation
                user._email = email
            else:
                raise InvalidInputException("Invalid email format")
    
    def _update_profile_data(self, profile: UserProfile, profile_data: Dict[str, Any]) -> None:
        """
        Update profile entity with form data.
        
        Args:
            profile: UserProfile entity to update
            profile_data: Form data containing profile updates
        """
        # Update skin type
        if 'skin_type' in profile_data and profile_data['skin_type']:
            profile._skin_type = profile_data['skin_type']
        
        # Update age range
        if 'age_range' in profile_data and profile_data['age_range']:
            profile._age_range = profile_data['age_range']
        
        # Update skin concerns
        if 'skin_concerns' in profile_data:
            concerns = [concern.strip() for concern in profile_data['skin_concerns'] if concern.strip()]
            profile._skin_concerns = concerns
        
        # Update dermatological conditions
        if 'dermatological_conditions' in profile_data:
            conditions = [condition.strip() for condition in profile_data['dermatological_conditions'] if condition.strip()]
            profile._dermatological_conditions = conditions
        
        # Update dermatological other
        if 'dermatological_other' in profile_data:
            profile._dermatological_other = profile_data['dermatological_other'].strip()
        
        # Update allergies
        if 'allergies' in profile_data:
            allergies = [allergy.strip() for allergy in profile_data['allergies'] if allergy.strip()]
            profile._allergies = allergies
        
        # Update allergies other
        if 'allergies_other' in profile_data:
            profile._allergies_other = profile_data['allergies_other'].strip()
        
        # Update product style
        if 'product_style' in profile_data and profile_data['product_style']:
            profile._product_style = profile_data['product_style']
        
        # Update routine frequency
        if 'routine_frequency' in profile_data and profile_data['routine_frequency']:
            profile._routine_frequency = profile_data['routine_frequency']
        
        # Update objectives
        if 'objectives' in profile_data:
            objectives = [objective.strip() for objective in profile_data['objectives'] if objective.strip()]
            profile._objectives = objectives
        
        # Update budget
        if 'budget' in profile_data and profile_data['budget']:
            profile._budget = profile_data['budget']
