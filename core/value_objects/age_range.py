"""
Age range value object for BeautyScan domain.

Represents age ranges with validation and business rules.
"""

from enum import Enum
from typing import List
from core.exceptions import InvalidAgeRangeError


class AgeRange(Enum):
    """Enumeration of valid age ranges."""
    
    UNDER_18 = "under18"
    AGE_18_25 = "18-25"
    AGE_26_35 = "26-35"
    AGE_36_45 = "36-45"
    AGE_46_60 = "46-60"
    AGE_60_PLUS = "60plus"
    UNSPECIFIED = ""
    
    @classmethod
    def from_string(cls, age_range: str) -> "AgeRange":
        """
        Create AgeRange from string value.
        
        Args:
            age_range: String representation of age range
            
        Returns:
            AgeRange enum value
            
        Raises:
            InvalidAgeRangeError: If age range is not valid
        """
        if not age_range:
            return cls.UNSPECIFIED
            
        try:
            return cls(age_range)
        except ValueError:
            valid_ranges = [r.value for r in cls if r != cls.UNSPECIFIED]
            raise InvalidAgeRangeError(
                f"Invalid age range '{age_range}'. Valid ranges are: {', '.join(valid_ranges)}"
            )
    
    @classmethod
    def get_all_valid_ranges(cls) -> List[str]:
        """
        Get all valid age range values.
        
        Returns:
            List of valid age range strings
        """
        return [r.value for r in cls if r != cls.UNSPECIFIED]
    
    def is_specified(self) -> bool:
        """
        Check if age range is specified (not empty).
        
        Returns:
            True if age range is specified, False otherwise
        """
        return self != self.UNSPECIFIED
    
    def get_display_name(self) -> str:
        """
        Get display name for the age range.
        
        Returns:
            Human-readable display name
        """
        display_names = {
            self.UNDER_18: "Moins de 18 ans",
            self.AGE_18_25: "18–25 ans",
            self.AGE_26_35: "26–35 ans",
            self.AGE_36_45: "36–45 ans",
            self.AGE_46_60: "46–60 ans",
            self.AGE_60_PLUS: "60+ ans",
            self.UNSPECIFIED: "Non spécifié"
        }
        return display_names[self]
    
    def get_min_age(self) -> int:
        """
        Get minimum age for this range.
        
        Returns:
            Minimum age in years
        """
        min_ages = {
            self.UNDER_18: 0,
            self.AGE_18_25: 18,
            self.AGE_26_35: 26,
            self.AGE_36_45: 36,
            self.AGE_46_60: 46,
            self.AGE_60_PLUS: 60,
            self.UNSPECIFIED: 0
        }
        return min_ages[self]
    
    def get_max_age(self) -> int:
        """
        Get maximum age for this range.
        
        Returns:
            Maximum age in years (999 for 60+)
        """
        max_ages = {
            self.UNDER_18: 17,
            self.AGE_18_25: 25,
            self.AGE_26_35: 35,
            self.AGE_36_45: 45,
            self.AGE_46_60: 60,
            self.AGE_60_PLUS: 999,
            self.UNSPECIFIED: 999
        }
        return max_ages[self]
