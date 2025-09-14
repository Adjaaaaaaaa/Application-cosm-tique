"""
User repository interface for BeautyScan application.

Defines the contract for user data access operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from core.entities.user import User
from core.exceptions import UserNotFoundError


class UserRepository(ABC):
    """
    Abstract repository for user data access.
    
    This interface defines the contract for user-related data operations
    without depending on specific implementation details (Django ORM, etc.).
    """
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User entity or None if not found
            
        Raises:
            UserNotFoundError: If user cannot be retrieved
        """
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User entity or None if not found
        """
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address
            
        Returns:
            User entity or None if not found
        """
        pass
    
    @abstractmethod
    def save(self, user: User) -> User:
        """
        Save user entity.
        
        Args:
            user: User entity to save
            
        Returns:
            Saved user entity with updated ID if new
            
        Raises:
            UserNotFoundError: If user cannot be saved
        """
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(self, user_id: int) -> bool:
        """
        Check if user exists.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user exists, False otherwise
        """
        pass
    
    @abstractmethod
    def get_all_active_users(self) -> List[User]:
        """
        Get all active users.
        
        Returns:
            List of active user entities
        """
        pass
