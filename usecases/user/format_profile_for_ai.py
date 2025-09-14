"""
Format profile for AI use case for BeautyScan application.

This use case handles formatting user profile data for AI consumption.
"""

from typing import Dict, Any
from core.entities.user import User
from core.entities.profile import UserProfile
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.exceptions import ProfileNotFoundError


class FormatProfileForAIUseCase:
    """
    Use case for formatting user profile data for AI prompts.
    
    This use case takes user profile data and formats it appropriately
    for AI consumption, ensuring proper structure and highlighting
    important information like allergies and medical conditions.
    """
    
    def execute(self, profile_data: Dict[str, Any]) -> str:
        """
        Execute the format profile for AI use case.
        
        Args:
            profile_data: Dictionary containing user profile data
            
        Returns:
            Formatted profile string for AI consumption
            
        Raises:
            ProfileNotFoundError: If profile data is invalid
        """
        if not profile_data:
            return "Profil utilisateur non disponible"
        
        try:
            # Convert dictionary to domain entities for proper formatting
            user = User(
                user_id=profile_data.get('user_id', 0),
                username=profile_data.get('username', 'utilisateur'),
                email=profile_data.get('email', ''),
                first_name=profile_data.get('first_name', ''),
                last_name=profile_data.get('last_name', ''),
                is_active=True
            )
            
            profile = UserProfile(
                user=user,
                skin_type=SkinType.from_string(profile_data.get('skin_type', '')),
                age_range=AgeRange.from_string(profile_data.get('age_range', '')),
                skin_concerns=profile_data.get('skin_concerns', []),
                dermatological_conditions=profile_data.get('dermatological_conditions', []),
                dermatological_other=profile_data.get('dermatological_other', ''),
                allergies=profile_data.get('allergies', []),
                allergies_other=profile_data.get('allergies_other', ''),
                product_style=profile_data.get('product_style', ''),
                routine_frequency=profile_data.get('routine_frequency', ''),
                objectives=profile_data.get('objectives', []),
                budget=profile_data.get('budget', ''),
                subscription_type=profile_data.get('subscription_type', 'free')
            )
            
            # Use domain entity formatting method
            return profile.format_for_ai()
            
        except Exception as e:
            raise ProfileNotFoundError(f"Error formatting profile for AI: {str(e)}")
    
    def execute_with_entities(self, profile: UserProfile) -> str:
        """
        Execute the use case with domain entities.
        
        Args:
            profile: UserProfile entity
            
        Returns:
            Formatted profile string for AI consumption
        """
        return profile.format_for_ai()
