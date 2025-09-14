"""
Payment service interface for BeautyScan application.

Defines the contract for payment and subscription operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.entities.user import User


class PaymentService(ABC):
    """
    Abstract service for payment operations.
    
    This interface defines the contract for payment-related operations
    like subscription management, payment processing, and billing.
    """
    
    @abstractmethod
    def create_subscription(
        self, 
        user: User, 
        subscription_type: str,
        payment_method_id: str
    ) -> Dict[str, Any]:
        """
        Create a new subscription for a user.
        
        Args:
            user: User entity
            subscription_type: Type of subscription (premium, pro)
            payment_method_id: Payment method identifier
            
        Returns:
            Dictionary containing subscription information
            
        Raises:
            PaymentError: If subscription creation fails
        """
        pass
    
    @abstractmethod
    def cancel_subscription(self, user: User) -> Dict[str, Any]:
        """
        Cancel user's subscription.
        
        Args:
            user: User entity
            
        Returns:
            Dictionary containing cancellation information
        """
        pass
    
    @abstractmethod
    def get_subscription_status(self, user: User) -> Dict[str, Any]:
        """
        Get user's subscription status.
        
        Args:
            user: User entity
            
        Returns:
            Dictionary containing subscription status
        """
        pass
    
    @abstractmethod
    def update_payment_method(
        self, 
        user: User, 
        payment_method_id: str
    ) -> Dict[str, Any]:
        """
        Update user's payment method.
        
        Args:
            user: User entity
            payment_method_id: New payment method identifier
            
        Returns:
            Dictionary containing update information
        """
        pass
    
    @abstractmethod
    def get_billing_history(self, user: User) -> List[Dict[str, Any]]:
        """
        Get user's billing history.
        
        Args:
            user: User entity
            
        Returns:
            List of billing records
        """
        pass
    
    @abstractmethod
    def is_premium_user(self, user: User) -> bool:
        """
        Check if user has premium access.
        
        Args:
            user: User entity
            
        Returns:
            True if user has premium access, False otherwise
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if payment service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get payment service information and status.
        
        Returns:
            Dictionary with service information
        """
        pass
