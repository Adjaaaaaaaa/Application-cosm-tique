"""
AI service interface for BeautyScan application.

Defines the contract for AI-related operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from core.entities.profile import UserProfile


class AIService(ABC):
    """
    Abstract service for AI operations.
    
    This interface defines the contract for AI-related operations
    like routine generation, ingredient analysis, and product recommendations.
    """
    
    @abstractmethod
    def generate_routine(
        self, 
        profile: UserProfile, 
        routine_type: str = "daily",
        custom_question: str = ""
    ) -> Dict[str, Any]:
        """
        Generate personalized skincare routine.
        
        Args:
            profile: User profile with preferences and concerns
            routine_type: Type of routine (daily, weekly, custom)
            custom_question: Custom question for routine generation
            
        Returns:
            Dictionary containing generated routine data
            
        Raises:
            RoutineGenerationError: If routine generation fails
        """
        pass
    
    @abstractmethod
    def analyze_ingredients(self, ingredients: List[str]) -> Dict[str, Any]:
        """
        Analyze cosmetic ingredients for safety and effectiveness.
        
        Args:
            ingredients: List of ingredient names
            
        Returns:
            Dictionary containing ingredient analysis results
        """
        pass
    
    @abstractmethod
    def get_ingredient_info(self, ingredient_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific ingredient.
        
        Args:
            ingredient_name: Name of the ingredient
            
        Returns:
            Dictionary containing ingredient information
        """
        pass
    
    @abstractmethod
    def answer_general_question(
        self, 
        question: str, 
        profile: Optional[UserProfile] = None
    ) -> Dict[str, Any]:
        """
        Answer general skincare questions.
        
        Args:
            question: User's question
            profile: Optional user profile for personalized answers
            
        Returns:
            Dictionary containing answer and related information
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if AI service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get AI service information and status.
        
        Returns:
            Dictionary with service information
        """
        pass
