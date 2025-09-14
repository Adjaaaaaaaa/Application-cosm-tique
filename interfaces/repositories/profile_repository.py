"""
User profile repository interface for BeautyScan application.

Defines the contract for user profile data access operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from core.entities.user import User
from core.entities.profile import UserProfile
from core.exceptions import ProfileNotFoundError


class ProfileRepository(ABC):
    """
    Abstract repository for user profile data access.
    
    This interface defines the contract for user profile-related data operations
    without depending on specific implementation details.
    """
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """
        Get user profile by user ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserProfile entity or None if not found
            
        Raises:
            ProfileNotFoundError: If profile cannot be retrieved
        """
        pass
    
    @abstractmethod
    def get_by_user(self, user: User) -> Optional[UserProfile]:
        """
        Get user profile by user entity.
        
        Args:
            user: User entity
            
        Returns:
            UserProfile entity or None if not found
        """
        pass
    
    @abstractmethod
    def save(self, profile: UserProfile) -> UserProfile:
        """
        Save user profile entity.
        
        Args:
            profile: UserProfile entity to save
            
        Returns:
            Saved UserProfile entity
            
        Raises:
            ProfileNotFoundError: If profile cannot be saved
        """
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """
        Delete user profile by user ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(self, user_id: int) -> bool:
        """
        Check if user profile exists.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if profile exists, False otherwise
        """
        pass
    
    @abstractmethod
    def get_premium_users(self) -> List[UserProfile]:
        """
        Get all users with premium or pro subscription.
        
        Returns:
            List of premium user profiles
        """
        pass
    
    @abstractmethod
    def get_users_by_skin_type(self, skin_type: str) -> List[UserProfile]:
        """
        Get users by skin type.
        
        Args:
            skin_type: Skin type to filter by
            
        Returns:
            List of user profiles with specified skin type
        """
        pass
    
    @abstractmethod
    def get_users_by_age_range(self, age_range: str) -> List[UserProfile]:
        """
        Get users by age range.
        
        Args:
            age_range: Age range to filter by
            
        Returns:
            List of user profiles with specified age range
        """
        pass
