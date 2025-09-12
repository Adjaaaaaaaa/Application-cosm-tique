"""
Custom exceptions for backend services.
"""

class AIServiceException(Exception):
    """Base exception for AI service errors."""
    pass


class BeautyScanException(Exception):
    """Base exception for BeautyScan application."""
    
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
