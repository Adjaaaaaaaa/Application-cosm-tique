"""
User profile domain entity for BeautyScan application.

Represents a user's skincare profile with preferences, concerns, and medical information.
"""

import json
from typing import List, Dict, Any, Optional
from core.entities.user import User
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.exceptions import ProfileNotFoundError, InvalidSkinTypeError, InvalidAgeRangeError


class UserProfile:
    """
    Domain entity representing a user's skincare profile.
    
    Contains all user preferences, skin concerns, allergies, and medical information
    needed for personalized skincare recommendations.
    """
    
    def __init__(
        self,
        user: User,
        skin_type: Optional[SkinType] = None,
        age_range: Optional[AgeRange] = None,
        skin_concerns: Optional[List[str]] = None,
        dermatological_conditions: Optional[List[str]] = None,
        dermatological_other: Optional[str] = None,
        allergies: Optional[List[str]] = None,
        allergies_other: Optional[str] = None,
        product_style: Optional[str] = None,
        routine_frequency: Optional[str] = None,
        objectives: Optional[List[str]] = None,
        budget: Optional[str] = None,
        subscription_type: str = "free"
    ):
        """
        Initialize user profile.
        
        Args:
            user: User entity
            skin_type: Type of skin
            age_range: Age range
            skin_concerns: List of skin concerns
            dermatological_conditions: List of dermatological conditions
            dermatological_other: Other dermatological conditions
            allergies: List of allergies
            allergies_other: Other allergies
            product_style: Preferred product style
            routine_frequency: Preferred routine frequency
            objectives: List of skincare objectives
            budget: Budget range
            subscription_type: Subscription type (free, premium, pro)
        """
        if not isinstance(user, User):
            raise ProfileNotFoundError("User must be a User entity")
        
        self._user = user
        self._skin_type = skin_type or SkinType.UNSPECIFIED
        self._age_range = age_range or AgeRange.UNSPECIFIED
        self._skin_concerns = skin_concerns or []
        self._dermatological_conditions = dermatological_conditions or []
        self._dermatological_other = dermatological_other or ""
        self._allergies = allergies or []
        self._allergies_other = allergies_other or ""
        self._product_style = product_style or ""
        self._routine_frequency = routine_frequency or ""
        self._objectives = objectives or []
        self._budget = budget or ""
        self._subscription_type = subscription_type
    
    @property
    def user(self) -> User:
        """Get associated user."""
        return self._user
    
    @property
    def skin_type(self) -> SkinType:
        """Get skin type."""
        return self._skin_type
    
    @property
    def age_range(self) -> AgeRange:
        """Get age range."""
        return self._age_range
    
    @property
    def skin_concerns(self) -> List[str]:
        """Get skin concerns."""
        return self._skin_concerns.copy()
    
    @property
    def dermatological_conditions(self) -> List[str]:
        """Get dermatological conditions."""
        return self._dermatological_conditions.copy()
    
    @property
    def dermatological_other(self) -> str:
        """Get other dermatological conditions."""
        return self._dermatological_other
    
    @property
    def allergies(self) -> List[str]:
        """Get allergies."""
        return self._allergies.copy()
    
    @property
    def allergies_other(self) -> str:
        """Get other allergies."""
        return self._allergies_other
    
    @property
    def product_style(self) -> str:
        """Get product style preference."""
        return self._product_style
    
    @property
    def routine_frequency(self) -> str:
        """Get routine frequency preference."""
        return self._routine_frequency
    
    @property
    def objectives(self) -> List[str]:
        """Get skincare objectives."""
        return self._objectives.copy()
    
    @property
    def budget(self) -> str:
        """Get budget preference."""
        return self._budget
    
    @property
    def subscription_type(self) -> str:
        """Get subscription type."""
        return self._subscription_type
    
    def is_premium(self) -> bool:
        """
        Check if user has premium access.
        
        Returns:
            True if user has premium or pro subscription, False otherwise
        """
        return self._subscription_type in ["premium", "pro"]
    
    def is_pro(self) -> bool:
        """
        Check if user has pro access.
        
        Returns:
            True if user has pro subscription, False otherwise
        """
        return self._subscription_type == "pro"
    
    def update_skin_type(self, skin_type: SkinType) -> None:
        """
        Update skin type.
        
        Args:
            skin_type: New skin type
        """
        self._skin_type = skin_type
    
    def update_age_range(self, age_range: AgeRange) -> None:
        """
        Update age range.
        
        Args:
            age_range: New age range
        """
        self._age_range = age_range
    
    def update_skin_concerns(self, concerns: List[str]) -> None:
        """
        Update skin concerns.
        
        Args:
            concerns: New list of skin concerns
        """
        self._skin_concerns = [concern.strip() for concern in concerns if concern and concern.strip()]
    
    def add_skin_concern(self, concern: str) -> None:
        """
        Add a skin concern.
        
        Args:
            concern: Skin concern to add
        """
        if concern and concern.strip() and concern.strip() not in self._skin_concerns:
            self._skin_concerns.append(concern.strip())
    
    def remove_skin_concern(self, concern: str) -> None:
        """
        Remove a skin concern.
        
        Args:
            concern: Skin concern to remove
        """
        if concern in self._skin_concerns:
            self._skin_concerns.remove(concern)
    
    def update_dermatological_conditions(self, conditions: List[str]) -> None:
        """
        Update dermatological conditions.
        
        Args:
            conditions: New list of dermatological conditions
        """
        self._dermatological_conditions = [condition.strip() for condition in conditions if condition and condition.strip()]
    
    def add_dermatological_condition(self, condition: str) -> None:
        """
        Add a dermatological condition.
        
        Args:
            condition: Condition to add
        """
        if condition and condition.strip() and condition.strip() not in self._dermatological_conditions:
            self._dermatological_conditions.append(condition.strip())
    
    def update_allergies(self, allergies: List[str]) -> None:
        """
        Update allergies.
        
        Args:
            allergies: New list of allergies
        """
        self._allergies = [allergy.strip() for allergy in allergies if allergy and allergy.strip()]
    
    def add_allergy(self, allergy: str) -> None:
        """
        Add an allergy.
        
        Args:
            allergy: Allergy to add
        """
        if allergy and allergy.strip() and allergy.strip() not in self._allergies:
            self._allergies.append(allergy.strip())
    
    def remove_allergy(self, allergy: str) -> None:
        """
        Remove an allergy.
        
        Args:
            allergy: Allergy to remove
        """
        if allergy in self._allergies:
            self._allergies.remove(allergy)
    
    def get_all_allergies(self) -> List[str]:
        """
        Get all allergies including other allergies.
        
        Returns:
            Combined list of allergies and other allergies
        """
        all_allergies = self._allergies.copy()
        if self._allergies_other and self._allergies_other.strip():
            all_allergies.append(self._allergies_other.strip())
        return all_allergies
    
    def update_objectives(self, objectives: List[str]) -> None:
        """
        Update skincare objectives.
        
        Args:
            objectives: New list of objectives
        """
        self._objectives = [objective.strip() for objective in objectives if objective and objective.strip()]
    
    def add_objective(self, objective: str) -> None:
        """
        Add a skincare objective.
        
        Args:
            objective: Objective to add
        """
        if objective and objective.strip() and objective.strip() not in self._objectives:
            self._objectives.append(objective.strip())
    
    def update_subscription_type(self, subscription_type: str) -> None:
        """
        Update subscription type.
        
        Args:
            subscription_type: New subscription type
        """
        valid_types = ["free", "premium", "pro"]
        if subscription_type not in valid_types:
            raise ProfileNotFoundError(f"Invalid subscription type: {subscription_type}")
        
        self._subscription_type = subscription_type
    
    def format_for_ai(self) -> str:
        """
        Format profile data for AI prompts.
        
        Returns:
            Formatted profile string for AI consumption
        """
        # Format allergies with warning emojis
        all_allergies = self.get_all_allergies()
        if all_allergies:
            allergies_text = "🚨 " + ", ".join(all_allergies) + " 🚨"
        else:
            allergies_text = "aucune"
        
        # Format skin concerns
        concerns_text = ", ".join(self._skin_concerns) if self._skin_concerns else "aucune"
        
        # Format dermatological conditions with warning emojis
        all_conditions = self._dermatological_conditions.copy()
        if self._dermatological_other and self._dermatological_other.strip():
            all_conditions.append(self._dermatological_other.strip())
        
        if all_conditions:
            conditions_text = "⚠️ " + ", ".join(all_conditions) + " ⚠️"
        else:
            conditions_text = "aucune"
        
        # Format objectives
        objectives_text = ", ".join(self._objectives) if self._objectives else "aucune"
        
        return f"""
**Profil Utilisateur:**
- **Nom:** {self._user.get_display_name()}
- **Type de peau:** {self._skin_type.get_display_name()}
- **Tranche d'âge:** {self._age_range.get_display_name()}
- **Allergies:** {allergies_text}
- **Préoccupations cutanées:** {concerns_text}
- **Objectifs:** {objectives_text}
- **Conditions dermatologiques:** {conditions_text}
- **Style de produits:** {self._product_style or 'pharmacy'}
- **Fréquence de routine:** {self._routine_frequency or 'standard'}
- **Budget:** {self._budget or 'moderate'}
        """.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert profile to dictionary.
        
        Returns:
            Dictionary representation of profile
        """
        return {
            'user_id': self._user.id,
            'username': self._user.username,
            'email': self._user.email,
            'first_name': self._user.first_name,
            'last_name': self._user.last_name,
            'skin_type': self._skin_type.value,
            'age_range': self._age_range.value,
            'skin_concerns': self._skin_concerns,
            'dermatological_conditions': self._dermatological_conditions,
            'dermatological_other': self._dermatological_other,
            'allergies': self._allergies,
            'allergies_other': self._allergies_other,
            'product_style': self._product_style,
            'routine_frequency': self._routine_frequency,
            'objectives': self._objectives,
            'budget': self._budget,
            'subscription_type': self._subscription_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], user: User) -> "UserProfile":
        """
        Create UserProfile from dictionary.
        
        Args:
            data: Dictionary containing profile data
            user: User entity
            
        Returns:
            UserProfile instance
        """
        skin_type = SkinType.from_string(data.get('skin_type', ''))
        age_range = AgeRange.from_string(data.get('age_range', ''))
        
        return cls(
            user=user,
            skin_type=skin_type,
            age_range=age_range,
            skin_concerns=data.get('skin_concerns', []),
            dermatological_conditions=data.get('dermatological_conditions', []),
            dermatological_other=data.get('dermatological_other', ''),
            allergies=data.get('allergies', []),
            allergies_other=data.get('allergies_other', ''),
            product_style=data.get('product_style', ''),
            routine_frequency=data.get('routine_frequency', ''),
            objectives=data.get('objectives', []),
            budget=data.get('budget', ''),
            subscription_type=data.get('subscription_type', 'free')
        )
    
    def __eq__(self, other) -> bool:
        """Check equality based on user ID."""
        if not isinstance(other, UserProfile):
            return False
        return self._user.id == other._user.id
    
    def __hash__(self) -> int:
        """Hash based on user ID."""
        return hash(self._user.id)
    
    def __str__(self) -> str:
        """String representation."""
        return f"UserProfile(user_id={self._user.id}, username='{self._user.username}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"UserProfile(user_id={self._user.id}, skin_type={self._skin_type.value}, "
            f"age_range={self._age_range.value}, subscription_type='{self._subscription_type}')"
        )
