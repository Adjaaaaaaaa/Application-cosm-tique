"""
User service for BeautyScan backend API.

Handles user profile retrieval and data formatting.
This service now uses Clean Architecture domain entities internally.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional

# Django imports will be handled dynamically
from .user_service_adapter import UserServiceAdapter

logger = logging.getLogger(__name__)


class UserService:
    """
    Service for user profile management and retrieval.
    
    This service maintains backward compatibility while using Clean Architecture
    domain entities internally through the UserServiceAdapter.
    """
    
    def __init__(self):
        """Initialize user service with Clean Architecture adapter."""
        self._adapter = UserServiceAdapter()
    
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
        return self._adapter.get_user_profile(user_id)
    

    def get_user_allergies(self, user_id: int) -> List[str]:
        """
        Get user allergies using Django ORM.
        
        Args:
            user_id: User ID
            
        Returns:
            List of allergy ingredient names
        """
        return self._adapter.get_user_allergies(user_id)
    
    def format_profile_for_ai(self, profile: Dict[str, Any]) -> str:
        """
        Format user profile for AI prompt.
        
        Args:
            profile: User profile dictionary
            
        Returns:
            Formatted profile string for AI
        """
        return self._adapter.format_profile_for_ai(profile)

