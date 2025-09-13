"""
Safety score value object for BeautyScan domain.

Represents product safety scores with validation and business rules.
"""

from decimal import Decimal
from enum import Enum
from typing import Optional
from core.exceptions import InvalidSafetyScoreError


class RiskLevel(Enum):
    """Enumeration of risk levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_string(cls, risk_level: str) -> "RiskLevel":
        """
        Create RiskLevel from string value.
        
        Args:
            risk_level: String representation of risk level
            
        Returns:
            RiskLevel enum value
        """
        if not risk_level:
            return cls.UNKNOWN
            
        try:
            return cls(risk_level.lower())
        except ValueError:
            valid_levels = [level.value for level in cls]
            raise InvalidSafetyScoreError(
                f"Invalid risk level '{risk_level}'. Valid levels are: {', '.join(valid_levels)}"
            )
    
    def get_display_name(self) -> str:
        """
        Get display name for the risk level.
        
        Returns:
            Human-readable display name
        """
        display_names = {
            self.LOW: "Faible",
            self.MEDIUM: "Moyen",
            self.HIGH: "Élevé",
            self.UNKNOWN: "Inconnu"
        }
        return display_names[self]
    
    def get_color_code(self) -> str:
        """
        Get color code for UI display.
        
        Returns:
            CSS color code
        """
        color_codes = {
            self.LOW: "#28a745",      # Green
            self.MEDIUM: "#ffc107",   # Yellow
            self.HIGH: "#dc3545",     # Red
            self.UNKNOWN: "#6c757d"   # Gray
        }
        return color_codes[self]


class SafetyScore:
    """
    Value object representing a product safety score.
    
    A safety score is defined by its numerical value and associated risk level.
    """
    
    MIN_SCORE = Decimal("0.0")
    MAX_SCORE = Decimal("100.0")
    
    def __init__(self, score: Decimal, risk_level: Optional[RiskLevel] = None):
        """
        Initialize safety score.
        
        Args:
            score: Numerical safety score (0.0 to 100.0)
            risk_level: Associated risk level
            
        Raises:
            InvalidSafetyScoreError: If score is invalid
        """
        if not isinstance(score, Decimal):
            try:
                score = Decimal(str(score))
            except (ValueError, TypeError):
                raise InvalidSafetyScoreError(f"Invalid score value: {score}")
        
        if score < self.MIN_SCORE or score > self.MAX_SCORE:
            raise InvalidSafetyScoreError(
                f"Score must be between {self.MIN_SCORE} and {self.MAX_SCORE}, got {score}"
            )
        
        self._score = score
        self._risk_level = risk_level or self._calculate_risk_level(score)
    
    def _calculate_risk_level(self, score: Decimal) -> RiskLevel:
        """
        Calculate risk level based on score.
        
        Args:
            score: Safety score
            
        Returns:
            Calculated risk level
        """
        if score >= Decimal("80.0"):
            return RiskLevel.LOW
        elif score >= Decimal("60.0"):
            return RiskLevel.MEDIUM
        elif score >= Decimal("0.0"):
            return RiskLevel.HIGH
        else:
            return RiskLevel.UNKNOWN
    
    @property
    def score(self) -> Decimal:
        """Get numerical safety score."""
        return self._score
    
    @property
    def risk_level(self) -> RiskLevel:
        """Get associated risk level."""
        return self._risk_level
    
    def get_percentage(self) -> float:
        """
        Get score as percentage.
        
        Returns:
            Score as percentage (0.0 to 100.0)
        """
        return float(self._score)
    
    def get_grade(self) -> str:
        """
        Get letter grade for the score.
        
        Returns:
            Letter grade (A, B, C, D, F)
        """
        if self._score >= Decimal("90.0"):
            return "A"
        elif self._score >= Decimal("80.0"):
            return "B"
        elif self._score >= Decimal("70.0"):
            return "C"
        elif self._score >= Decimal("60.0"):
            return "D"
        else:
            return "F"
    
    def is_safe(self) -> bool:
        """
        Check if score indicates safe product.
        
        Returns:
            True if score is 80 or above, False otherwise
        """
        return self._score >= Decimal("80.0")
    
    def is_high_risk(self) -> bool:
        """
        Check if score indicates high risk product.
        
        Returns:
            True if score is below 60, False otherwise
        """
        return self._score < Decimal("60.0")
    
    def get_display_text(self) -> str:
        """
        Get display text for the safety score.
        
        Returns:
            Human-readable display text
        """
        return f"{self._score}/100 ({self._risk_level.get_display_name()})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on score."""
        if not isinstance(other, SafetyScore):
            return False
        return self._score == other._score
    
    def __lt__(self, other) -> bool:
        """Check if this score is less than another."""
        if not isinstance(other, SafetyScore):
            return NotImplemented
        return self._score < other._score
    
    def __le__(self, other) -> bool:
        """Check if this score is less than or equal to another."""
        if not isinstance(other, SafetyScore):
            return NotImplemented
        return self._score <= other._score
    
    def __gt__(self, other) -> bool:
        """Check if this score is greater than another."""
        if not isinstance(other, SafetyScore):
            return NotImplemented
        return self._score > other._score
    
    def __ge__(self, other) -> bool:
        """Check if this score is greater than or equal to another."""
        if not isinstance(other, SafetyScore):
            return NotImplemented
        return self._score >= other._score
    
    def __str__(self) -> str:
        """String representation."""
        return self.get_display_text()
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"SafetyScore(score={self._score}, risk_level={self._risk_level})"
