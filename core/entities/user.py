"""
User domain entity for BeautyScan application.

Represents a user with their identity and basic information.
"""

from typing import Optional
from core.exceptions import UserNotFoundError


class User:
    """
    Domain entity representing a user.
    
    A user is defined by their unique identifier and basic information.
    """
    
    def __init__(
        self,
        user_id: int,
        username: str,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        is_active: bool = True
    ):
        """
        Initialize user entity.
        
        Args:
            user_id: Unique user identifier
            username: Username
            email: Email address
            first_name: First name (optional)
            last_name: Last name (optional)
            is_active: Whether user is active (default: True)
            
        Raises:
            UserNotFoundError: If required fields are missing
        """
        if not user_id or user_id <= 0:
            raise UserNotFoundError("User ID must be a positive integer")
        
        if not username or not username.strip():
            raise UserNotFoundError("Username cannot be empty")
        
        if not email or not email.strip():
            raise UserNotFoundError("Email cannot be empty")
        
        self._id = user_id
        self._username = username.strip()
        self._email = email.strip()
        self._first_name = first_name.strip() if first_name else ""
        self._last_name = last_name.strip() if last_name else ""
        self._is_active = is_active
    
    @property
    def id(self) -> int:
        """Get user ID."""
        return self._id
    
    @property
    def username(self) -> str:
        """Get username."""
        return self._username
    
    @property
    def email(self) -> str:
        """Get email address."""
        return self._email
    
    @property
    def first_name(self) -> str:
        """Get first name."""
        return self._first_name
    
    @property
    def last_name(self) -> str:
        """Get last name."""
        return self._last_name
    
    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self._is_active
    
    def get_full_name(self) -> str:
        """
        Get user's full name.
        
        Returns:
            Full name combining first and last name
        """
        if self._first_name and self._last_name:
            return f"{self._first_name} {self._last_name}"
        elif self._first_name:
            return self._first_name
        elif self._last_name:
            return self._last_name
        else:
            return self._username
    
    def get_display_name(self) -> str:
        """
        Get display name for the user.
        
        Returns:
            Best available display name
        """
        full_name = self.get_full_name()
        return full_name if full_name != self._username else self._username
    
    def update_email(self, new_email: str) -> None:
        """
        Update user's email address.
        
        Args:
            new_email: New email address
            
        Raises:
            UserNotFoundError: If email is invalid
        """
        if not new_email or not new_email.strip():
            raise UserNotFoundError("Email cannot be empty")
        
        self._email = new_email.strip()
    
    def update_name(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> None:
        """
        Update user's name.
        
        Args:
            first_name: New first name (optional)
            last_name: New last name (optional)
        """
        if first_name is not None:
            self._first_name = first_name.strip() if first_name else ""
        
        if last_name is not None:
            self._last_name = last_name.strip() if last_name else ""
    
    def deactivate(self) -> None:
        """Deactivate the user."""
        self._is_active = False
    
    def activate(self) -> None:
        """Activate the user."""
        self._is_active = True
    
    def __eq__(self, other) -> bool:
        """Check equality based on user ID."""
        if not isinstance(other, User):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on user ID."""
        return hash(self._id)
    
    def __str__(self) -> str:
        """String representation."""
        return f"User(id={self._id}, username='{self._username}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"User(id={self._id}, username='{self._username}', "
            f"email='{self._email}', is_active={self._is_active})"
        )
