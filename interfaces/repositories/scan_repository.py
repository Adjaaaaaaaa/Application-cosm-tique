"""
Scan repository interface for BeautyScan application.

Defines the contract for scan data access operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from core.entities.user import User
from core.entities.scan import Scan
from core.exceptions import ScanNotFoundError


class ScanRepository(ABC):
    """
    Abstract repository for scan data access.
    
    This interface defines the contract for scan-related data operations
    without depending on specific implementation details.
    """
    
    @abstractmethod
    def get_by_id(self, scan_id: int) -> Optional[Scan]:
        """
        Get scan by ID.
        
        Args:
            scan_id: Scan identifier
            
        Returns:
            Scan entity or None if not found
            
        Raises:
            ScanNotFoundError: If scan cannot be retrieved
        """
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Scan]:
        """
        Get all scans for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of scan entities for the user
        """
        pass
    
    @abstractmethod
    def get_by_user(self, user: User) -> List[Scan]:
        """
        Get all scans for a user entity.
        
        Args:
            user: User entity
            
        Returns:
            List of scan entities for the user
        """
        pass
    
    @abstractmethod
    def save(self, scan: Scan) -> Scan:
        """
        Save scan entity.
        
        Args:
            scan: Scan entity to save
            
        Returns:
            Saved scan entity with updated ID if new
            
        Raises:
            ScanNotFoundError: If scan cannot be saved
        """
        pass
    
    @abstractmethod
    def delete(self, scan_id: int) -> bool:
        """
        Delete scan by ID.
        
        Args:
            scan_id: Scan identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(self, scan_id: int) -> bool:
        """
        Check if scan exists.
        
        Args:
            scan_id: Scan identifier
            
        Returns:
            True if scan exists, False otherwise
        """
        pass
    
    @abstractmethod
    def get_recent_scans(self, user_id: int, limit: int = 10) -> List[Scan]:
        """
        Get recent scans for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of scans to return
            
        Returns:
            List of recent scan entities
        """
        pass
    
    @abstractmethod
    def get_scans_by_type(self, user_id: int, scan_type: str) -> List[Scan]:
        """
        Get scans by type for a user.
        
        Args:
            user_id: User identifier
            scan_type: Type of scan (barcode, image, manual)
            
        Returns:
            List of scan entities with specified type
        """
        pass
    
    @abstractmethod
    def get_scans_with_analysis(self, user_id: int) -> List[Scan]:
        """
        Get scans that have analysis results.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of scan entities with analysis available
        """
        pass
    
    @abstractmethod
    def get_scans_by_date_range(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Scan]:
        """
        Get scans within a date range.
        
        Args:
            user_id: User identifier
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of scan entities within date range
        """
        pass
    
    @abstractmethod
    def count_by_user(self, user_id: int) -> int:
        """
        Count total scans for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Total number of scans for the user
        """
        pass
