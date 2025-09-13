"""
Skin type value object for BeautyScan domain.

Represents the different types of skin with validation and business rules.
"""

from enum import Enum
from typing import List
from core.exceptions import InvalidSkinTypeError


class SkinType(Enum):
    """Enumeration of valid skin types."""
    
    NORMAL = "normal"
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    UNSPECIFIED = ""
    
    @classmethod
    def from_string(cls, skin_type: str) -> "SkinType":
        """
        Create SkinType from string value.
        
        Args:
            skin_type: String representation of skin type
            
        Returns:
            SkinType enum value
            
        Raises:
            InvalidSkinTypeError: If skin type is not valid
        """
        if not skin_type:
            return cls.UNSPECIFIED
            
        try:
            return cls(skin_type)
        except ValueError:
            valid_types = [t.value for t in cls if t != cls.UNSPECIFIED]
            raise InvalidSkinTypeError(
                f"Invalid skin type '{skin_type}'. Valid types are: {', '.join(valid_types)}"
            )
    
    @classmethod
    def get_all_valid_types(cls) -> List[str]:
        """
        Get all valid skin type values.
        
        Returns:
            List of valid skin type strings
        """
        return [t.value for t in cls if t != cls.UNSPECIFIED]
    
    def is_specified(self) -> bool:
        """
        Check if skin type is specified (not empty).
        
        Returns:
            True if skin type is specified, False otherwise
        """
        return self != self.UNSPECIFIED
    
    def get_display_name(self) -> str:
        """
        Get display name for the skin type.
        
        Returns:
            Human-readable display name
        """
        display_names = {
            self.NORMAL: "Normal",
            self.DRY: "Sèche",
            self.OILY: "Grasse", 
            self.COMBINATION: "Mixte",
            self.SENSITIVE: "Sensible",
            self.UNSPECIFIED: "Non spécifié"
        }
        return display_names[self]
