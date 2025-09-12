"""
User profile management for BeautyScan.

Handles user skin profiles, preferences, and cosmetic needs.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class SkinType(Enum):
    """Skin types for cosmetic recommendations."""
    NORMAL = "normal"
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    MATURE = "mature"


class ProductCategory(Enum):
    """Product categories for cosmetic recommendations."""
    CLEANSER = "cleanser"
    MOISTURIZER = "moisturizer"
    SERUM = "serum"
    SUNSCREEN = "sunscreen"
    EXFOLIANT = "exfoliant"
    MASK = "mask"
    TONER = "toner"
    EYE_CREAM = "eye_cream"
    LIP_BALM = "lip_balm"
    BODY_LOTION = "body_lotion"
    SHAMPOO = "shampoo"
    CONDITIONER = "conditioner"
    BODY_WASH = "body_wash"


class AgeRange(Enum):
    """Age ranges for cosmetic recommendations."""
    TEEN = "13-17"
    YOUNG_ADULT = "18-25"
    ADULT = "26-35"
    MATURE = "36-45"
    SENIOR = "46+"


class SkinConcern(Enum):
    """Common skin concerns."""
    ACNE = "acne"
    AGING = "aging"
    DRYNESS = "dryness"
    OILINESS = "oiliness"
    SENSITIVITY = "sensitivity"
    HYPERPIGMENTATION = "hyperpigmentation"
    ROSACEA = "rosacea"
    LARGE_PORES = "large_pores"


@dataclass
class UserProfile:
    """User skin profile with preferences and needs."""
    
    # Basic information
    user_id: int
    username: str
    age: int
    skin_type: SkinType
    
    # Skin concerns and preferences
    skin_concerns: List[SkinConcern]
    allergies: List[str]
    preferences: List[str]  # e.g., ["vegan", "fragrance_free", "cruelty_free"]
    
    # Budget and routine preferences
    budget_range: str  # "low", "medium", "high"
    routine_complexity: str  # "simple", "moderate", "advanced"
    time_available: str  # "5min", "10min", "15min+"
    
    # Environmental factors
    climate: str  # "dry", "humid", "cold", "hot"
    sun_exposure: str  # "low", "moderate", "high"
    
    # Additional information
    pregnancy_breastfeeding: bool = False
    medications: List[str] = None
    previous_reactions: List[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.medications is None:
            self.medications = []
        if self.previous_reactions is None:
            self.previous_reactions = []
    
    def get_age_range(self) -> AgeRange:
        """Get age range category."""
        try:
            if self.age < 18:
                return AgeRange.TEEN
            elif self.age < 26:
                return AgeRange.YOUNG_ADULT
            elif self.age < 36:
                return AgeRange.ADULT
            elif self.age < 46:
                return AgeRange.MATURE
            else:
                return AgeRange.SENIOR
        except Exception:
            return AgeRange.ADULT
    
    def get_budget_amount(self) -> float:
        """Convert budget range to amount."""
        try:
            budget_map = {
                "low": 30.0,
                "medium": 80.0,
                "high": 150.0
            }
            return budget_map.get(self.budget_range, 50.0)
        except Exception:
            return 50.0
    
    def get_routine_steps_count(self) -> int:
        """Get number of steps based on complexity."""
        try:
            complexity_map = {
                "simple": 2,
                "moderate": 4,
                "advanced": 6
            }
            return complexity_map.get(self.routine_complexity, 3)
        except Exception:
            return 3
    
    def has_allergy_to(self, ingredient: str) -> bool:
        """Check if user is allergic to specific ingredient."""
        ingredient_lower = ingredient.lower()
        return any(allergy.lower() in ingredient_lower or ingredient_lower in allergy.lower() 
                  for allergy in self.allergies)
    
    def has_concern(self, concern: SkinConcern) -> bool:
        """Check if user has specific skin concern."""
        return concern in self.skin_concerns
    
    def is_sensitive_skin(self) -> bool:
        """Check if user has sensitive skin."""
        return (self.skin_type == SkinType.SENSITIVE or 
                SkinConcern.SENSITIVITY in self.skin_concerns)
    
    def needs_anti_aging(self) -> bool:
        """Check if user needs anti-aging products."""
        return (self.age >= 25 or 
                SkinConcern.AGING in self.skin_concerns)
    
    def needs_acne_treatment(self) -> bool:
        """Check if user needs acne treatment."""
        return SkinConcern.ACNE in self.skin_concerns
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "age": self.age,
            "age_range": self.get_age_range().value,
            "skin_type": self.skin_type.value,
            "skin_concerns": [concern.value for concern in self.skin_concerns],
            "allergies": self.allergies,
            "preferences": self.preferences,
            "budget_range": self.budget_range,
            "budget_amount": self.get_budget_amount(),
            "routine_complexity": self.routine_complexity,
            "time_available": self.time_available,
            "climate": self.climate,
            "sun_exposure": self.sun_exposure,
            "pregnancy_breastfeeding": self.pregnancy_breastfeeding,
            "medications": self.medications,
            "previous_reactions": self.previous_reactions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create profile from dictionary."""
        return cls(
            user_id=data.get("user_id", 1),
            username=data.get("username", "user"),
            age=data.get("age", 25),
            skin_type=SkinType(data.get("skin_type", "normal")),
            skin_concerns=[SkinConcern(concern) for concern in data.get("skin_concerns", [])],
            allergies=data.get("allergies", []),
            preferences=data.get("preferences", []),
            budget_range=data.get("budget_range", "medium"),
            routine_complexity=data.get("routine_complexity", "moderate"),
            time_available=data.get("time_available", "10min"),
            climate=data.get("climate", "temperate"),
            sun_exposure=data.get("sun_exposure", "moderate"),
            pregnancy_breastfeeding=data.get("pregnancy_breastfeeding", False),
            medications=data.get("medications", []),
            previous_reactions=data.get("previous_reactions", [])
        )


class UserProfileManager:
    """Manager for user profile operations."""
    
    def __init__(self):
        """Initialize profile manager."""
        self.profiles: Dict[int, UserProfile] = {}
    
    def create_profile(self, profile: UserProfile) -> bool:
        """Create a new user profile."""
        try:
            self.profiles[profile.user_id] = profile
            return True
        except Exception:
            return False
    
    def get_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by ID."""
        return self.profiles.get(user_id)
    
    def update_profile(self, user_id: int, updates: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile with new information."""
        try:
            profile = self.get_profile(user_id)
            if not profile:
                return None
            
            # Update profile fields
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            self.profiles[user_id] = profile
            return profile
        except Exception:
            return None
    
    def delete_profile(self, user_id: int) -> bool:
        """Delete user profile."""
        try:
            if user_id in self.profiles:
                del self.profiles[user_id]
                return True
            return False
        except Exception:
            return False
    
    def get_default_profile(self, user_id: int = 1, username: str = "default_user") -> UserProfile:
        """Get default profile for new users."""
        return UserProfile(
            user_id=user_id,
            username=username,
            age=25,
            skin_type=SkinType.NORMAL,
            skin_concerns=[],
            allergies=[],
            preferences=[],
            budget_range="medium",
            routine_complexity="moderate",
            time_available="10min",
            climate="temperate",
            sun_exposure="moderate",
            pregnancy_breastfeeding=False,
            medications=[],
            previous_reactions=[]
        )
    
    def get_all_profiles(self) -> List[UserProfile]:
        """Get all user profiles."""
        return list(self.profiles.values())
    
    def search_profiles(self, criteria: Dict[str, Any]) -> List[UserProfile]:
        """Search profiles by criteria."""
        results = []
        for profile in self.profiles.values():
            match = True
            for key, value in criteria.items():
                if hasattr(profile, key):
                    profile_value = getattr(profile, key)
                    if profile_value != value:
                        match = False
                        break
                else:
                    match = False
                    break
            if match:
                results.append(profile)
        return results
