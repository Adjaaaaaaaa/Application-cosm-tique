"""
Scan domain entity for BeautyScan application.

Represents a product scan with analysis results and metadata.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from core.entities.user import User
from core.value_objects.safety_score import SafetyScore
from core.exceptions import ScanNotFoundError


class ScanType:
    """Enumeration of scan types."""
    
    BARCODE = "barcode"
    IMAGE = "image"
    MANUAL = "manual"
    
    @classmethod
    def is_valid(cls, scan_type: str) -> bool:
        """
        Check if scan type is valid.
        
        Args:
            scan_type: Scan type to validate
            
        Returns:
            True if valid, False otherwise
        """
        return scan_type in [cls.BARCODE, cls.IMAGE, cls.MANUAL]


class Scan:
    """
    Domain entity representing a product scan.
    
    Contains scan metadata, product information, and analysis results.
    """
    
    def __init__(
        self,
        scan_id: Optional[int],
        user: User,
        scan_type: str,
        barcode: Optional[str] = None,
        image_path: Optional[str] = None,
        notes: Optional[str] = None,
        scanned_at: Optional[datetime] = None,
        # Product information
        product_name: Optional[str] = None,
        product_brand: Optional[str] = None,
        product_description: Optional[str] = None,
        product_ingredients_text: Optional[str] = None,
        # Analysis results
        safety_score: Optional[SafetyScore] = None,
        analysis_available: bool = False
    ):
        """
        Initialize scan entity.
        
        Args:
            scan_id: Unique scan identifier (None for new scans)
            user: User who performed the scan
            scan_type: Type of scan (barcode, image, manual)
            barcode: Scanned barcode (optional)
            image_path: Path to uploaded image (optional)
            notes: User notes (optional)
            scanned_at: When scan was performed (default: now)
            product_name: Name of scanned product
            product_brand: Brand of scanned product
            product_description: Product description
            product_ingredients_text: Raw ingredients text
            safety_score: Calculated safety score
            analysis_available: Whether analysis is available
            
        Raises:
            ScanNotFoundError: If required fields are invalid
        """
        if not isinstance(user, User):
            raise ScanNotFoundError("User must be a User entity")
        
        if not ScanType.is_valid(scan_type):
            raise ScanNotFoundError(f"Invalid scan type: {scan_type}")
        
        if scan_type == ScanType.BARCODE and not barcode:
            raise ScanNotFoundError("Barcode is required for barcode scans")
        
        if scan_type == ScanType.IMAGE and not image_path:
            raise ScanNotFoundError("Image path is required for image scans")
        
        self._id = scan_id
        self._user = user
        self._scan_type = scan_type
        self._barcode = barcode or ""
        self._image_path = image_path or ""
        self._notes = notes or ""
        self._scanned_at = scanned_at or datetime.now()
        
        # Product information
        self._product_name = product_name or ""
        self._product_brand = product_brand or ""
        self._product_description = product_description or ""
        self._product_ingredients_text = product_ingredients_text or ""
        
        # Analysis results
        self._safety_score = safety_score
        self._analysis_available = analysis_available
    
    @property
    def id(self) -> Optional[int]:
        """Get scan ID."""
        return self._id
    
    @property
    def user(self) -> User:
        """Get user who performed the scan."""
        return self._user
    
    @property
    def scan_type(self) -> str:
        """Get scan type."""
        return self._scan_type
    
    @property
    def barcode(self) -> str:
        """Get scanned barcode."""
        return self._barcode
    
    @property
    def image_path(self) -> str:
        """Get image path."""
        return self._image_path
    
    @property
    def notes(self) -> str:
        """Get user notes."""
        return self._notes
    
    @property
    def scanned_at(self) -> datetime:
        """Get scan timestamp."""
        return self._scanned_at
    
    @property
    def product_name(self) -> str:
        """Get product name."""
        return self._product_name
    
    @property
    def product_brand(self) -> str:
        """Get product brand."""
        return self._product_brand
    
    @property
    def product_description(self) -> str:
        """Get product description."""
        return self._product_description
    
    @property
    def product_ingredients_text(self) -> str:
        """Get product ingredients text."""
        return self._product_ingredients_text
    
    @property
    def safety_score(self) -> Optional[SafetyScore]:
        """Get safety score."""
        return self._safety_score
    
    @property
    def analysis_available(self) -> bool:
        """Check if analysis is available."""
        return self._analysis_available
    
    def is_new(self) -> bool:
        """
        Check if this is a new scan (not yet persisted).
        
        Returns:
            True if scan ID is None, False otherwise
        """
        return self._id is None
    
    def has_product_info(self) -> bool:
        """
        Check if scan has product information.
        
        Returns:
            True if product name is available, False otherwise
        """
        return bool(self._product_name and self._product_name.strip())
    
    def has_ingredients(self) -> bool:
        """
        Check if scan has ingredient information.
        
        Returns:
            True if ingredients text is available, False otherwise
        """
        return bool(self._product_ingredients_text and self._product_ingredients_text.strip())
    
    def has_analysis(self) -> bool:
        """
        Check if scan has analysis results.
        
        Returns:
            True if analysis is available and safety score exists, False otherwise
        """
        return self._analysis_available and self._safety_score is not None
    
    def update_product_info(
        self,
        name: Optional[str] = None,
        brand: Optional[str] = None,
        description: Optional[str] = None,
        ingredients_text: Optional[str] = None
    ) -> None:
        """
        Update product information.
        
        Args:
            name: Product name
            brand: Product brand
            description: Product description
            ingredients_text: Ingredients text
        """
        if name is not None:
            self._product_name = name or ""
        if brand is not None:
            self._product_brand = brand or ""
        if description is not None:
            self._product_description = description or ""
        if ingredients_text is not None:
            self._product_ingredients_text = ingredients_text or ""
    
    def update_analysis(self, safety_score: SafetyScore) -> None:
        """
        Update analysis results.
        
        Args:
            safety_score: Calculated safety score
        """
        self._safety_score = safety_score
        self._analysis_available = True
    
    def clear_analysis(self) -> None:
        """Clear analysis results."""
        self._safety_score = None
        self._analysis_available = False
    
    def update_notes(self, notes: str) -> None:
        """
        Update user notes.
        
        Args:
            notes: New notes
        """
        self._notes = notes or ""
    
    def get_product_display_name(self) -> str:
        """
        Get display name for the product.
        
        Returns:
            Product name or "Produit inconnu" if not available
        """
        if self._product_name and self._product_name.strip():
            if self._product_brand and self._product_brand.strip():
                return f"{self._product_brand} - {self._product_name}"
            return self._product_name
        return "Produit inconnu"
    
    def get_ingredients_list(self) -> list:
        """
        Get ingredients as a list.
        
        Returns:
            List of ingredients parsed from ingredients text
        """
        if not self._product_ingredients_text:
            return []
        
        # Simple parsing - split by common separators
        ingredients = []
        for separator in [',', ';', '\n']:
            if separator in self._product_ingredients_text:
                ingredients = [
                    ingredient.strip() 
                    for ingredient in self._product_ingredients_text.split(separator)
                    if ingredient.strip()
                ]
                break
        
        return ingredients
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert scan to dictionary.
        
        Returns:
            Dictionary representation of scan
        """
        return {
            'id': self._id,
            'user_id': self._user.id,
            'scan_type': self._scan_type,
            'barcode': self._barcode,
            'image_path': self._image_path,
            'notes': self._notes,
            'scanned_at': self._scanned_at.isoformat(),
            'product_name': self._product_name,
            'product_brand': self._product_brand,
            'product_description': self._product_description,
            'product_ingredients_text': self._product_ingredients_text,
            'safety_score': float(self._safety_score.score) if self._safety_score else None,
            'risk_level': self._safety_score.risk_level.value if self._safety_score else None,
            'analysis_available': self._analysis_available
        }
    
    def __eq__(self, other) -> bool:
        """Check equality based on scan ID."""
        if not isinstance(other, Scan):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on scan ID."""
        return hash(self._id) if self._id else 0
    
    def __str__(self) -> str:
        """String representation."""
        return f"Scan(id={self._id}, user='{self._user.username}', product='{self.get_product_display_name()}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"Scan(id={self._id}, user_id={self._user.id}, scan_type='{self._scan_type}', "
            f"product_name='{self._product_name}', analysis_available={self._analysis_available})"
        )
