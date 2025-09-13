"""
Domain exceptions for BeautyScan application.

These exceptions represent business rule violations and domain-specific errors.
"""


class DomainException(Exception):
    """Base exception for domain-related errors."""
    pass


class UserNotFoundError(DomainException):
    """Raised when a user cannot be found."""
    pass


class ProfileNotFoundError(DomainException):
    """Raised when a user profile cannot be found."""
    pass


class InvalidSkinTypeError(DomainException):
    """Raised when an invalid skin type is provided."""
    pass


class InvalidAgeRangeError(DomainException):
    """Raised when an invalid age range is provided."""
    pass


class InvalidIngredientError(DomainException):
    """Raised when an invalid ingredient is provided."""
    pass


class InvalidSafetyScoreError(DomainException):
    """Raised when an invalid safety score is calculated."""
    pass


class ProductNotFoundError(DomainException):
    """Raised when a product cannot be found."""
    pass


class ScanNotFoundError(DomainException):
    """Raised when a scan cannot be found."""
    pass


class RoutineGenerationError(DomainException):
    """Raised when routine generation fails."""
    pass


class PremiumAccessDeniedError(DomainException):
    """Raised when premium access is denied."""
    pass
