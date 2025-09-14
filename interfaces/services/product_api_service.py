"""
Product API service interface for BeautyScan application.

Defines the contract for product data retrieval operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class ProductAPIService(ABC):
    """
    Abstract service for product data retrieval.
    
    This interface defines the contract for product-related operations
    like barcode lookup, product search, and ingredient information.
    """
    
    @abstractmethod
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Get product information by barcode.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Dictionary containing product information or None if not found
        """
        pass
    
    @abstractmethod
    def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for products by name or brand.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of product dictionaries
        """
        pass
    
    @abstractmethod
    def get_ingredient_safety_data(self, ingredient_name: str) -> Optional[Dict[str, Any]]:
        """
        Get safety data for an ingredient.
        
        Args:
            ingredient_name: Name of the ingredient
            
        Returns:
            Dictionary containing safety data or None if not found
        """
        pass
    
    @abstractmethod
    def get_ingredient_benefits(self, ingredient_name: str) -> List[str]:
        """
        Get benefits of an ingredient.
        
        Args:
            ingredient_name: Name of the ingredient
            
        Returns:
            List of ingredient benefits
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if product API service is available.
        
        Returns:
            True if service is available, False otherwise
        """
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get product API service information and status.
        
        Returns:
            Dictionary with service information
        """
        pass
