"""
Django ORM implementation of ScanRepository.

This repository implements the ScanRepository interface using Django ORM.
"""

import logging
from typing import Optional, List
from datetime import datetime
from django.contrib.auth.models import User as DjangoUser
from apps.scans.models import Scan as DjangoScan

from core.entities.user import User
from core.entities.scan import Scan
from core.value_objects.safety_score import SafetyScore
from core.exceptions import ScanNotFoundError
from interfaces.repositories.scan_repository import ScanRepository

logger = logging.getLogger(__name__)


class DjangoScanRepository(ScanRepository):
    """
    Django ORM implementation of ScanRepository.
    
    This repository provides concrete implementation of scan data access
    operations using Django's ORM.
    """
    
    def get_by_id(self, scan_id: int) -> Optional[Scan]:
        """
        Get scan by ID using Django ORM.
        
        Args:
            scan_id: Scan identifier
            
        Returns:
            Scan entity or None if not found
        """
        try:
            django_scan = DjangoScan.objects.get(id=scan_id)
            return self._to_domain_entity(django_scan)
        except DjangoScan.DoesNotExist:
            logger.warning(f"Scan with ID {scan_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving scan {scan_id}: {str(e)}")
            raise ScanNotFoundError(f"Error retrieving scan {scan_id}: {str(e)}")
    
    def get_by_user_id(self, user_id: int) -> List[Scan]:
        """
        Get all scans for a user using Django ORM.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of scan entities for the user
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            django_scans = DjangoScan.objects.filter(user=django_user).order_by('-scanned_at')
            return [self._to_domain_entity(scan) for scan in django_scans]
        except DjangoUser.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found")
            return []
        except Exception as e:
            logger.error(f"Error retrieving scans for user {user_id}: {str(e)}")
            raise ScanNotFoundError(f"Error retrieving scans for user {user_id}: {str(e)}")
    
    def get_by_user(self, user: User) -> List[Scan]:
        """
        Get all scans for a user entity using Django ORM.
        
        Args:
            user: User entity
            
        Returns:
            List of scan entities for the user
        """
        return self.get_by_user_id(user.id)
    
    def save(self, scan: Scan) -> Scan:
        """
        Save scan entity using Django ORM.
        
        Args:
            scan: Scan entity to save
            
        Returns:
            Saved scan entity with updated ID if new
        """
        try:
            django_user = DjangoUser.objects.get(id=scan.user.id)
            
            if scan.id and scan.id > 0:
                # Update existing scan
                django_scan = DjangoScan.objects.get(id=scan.id)
                self._update_django_scan(django_scan, scan)
                django_scan.save()
                logger.info(f"Updated scan {scan.id}")
            else:
                # Create new scan
                django_scan = DjangoScan.objects.create(
                    user=django_user,
                    scan_type=scan.scan_type,
                    barcode=scan.barcode,
                    image=scan.image_path,
                    scanned_at=scan.scanned_at,
                    notes=scan.notes,
                    product_name=scan.product_name,
                    product_brand=scan.product_brand,
                    product_description=scan.product_description,
                    product_ingredients_text=scan.product_ingredients_text,
                    product_score=scan.safety_score.score if scan.safety_score else None,
                    product_risk_level=scan.safety_score.risk_level if scan.safety_score else '',
                    analysis_available=scan.analysis_available
                )
                logger.info(f"Created new scan {django_scan.id}")
            
            return self._to_domain_entity(django_scan)
            
        except DjangoUser.DoesNotExist:
            logger.error(f"User {scan.user.id} not found for scan save")
            raise ScanNotFoundError(f"User {scan.user.id} not found")
        except Exception as e:
            logger.error(f"Error saving scan: {str(e)}")
            raise ScanNotFoundError(f"Error saving scan: {str(e)}")
    
    def delete(self, scan_id: int) -> bool:
        """
        Delete scan by ID using Django ORM.
        
        Args:
            scan_id: Scan identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            django_scan = DjangoScan.objects.get(id=scan_id)
            django_scan.delete()
            logger.info(f"Deleted scan {scan_id}")
            return True
        except DjangoScan.DoesNotExist:
            logger.warning(f"Scan {scan_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting scan {scan_id}: {str(e)}")
            raise ScanNotFoundError(f"Error deleting scan {scan_id}: {str(e)}")
    
    def exists(self, scan_id: int) -> bool:
        """
        Check if scan exists using Django ORM.
        
        Args:
            scan_id: Scan identifier
            
        Returns:
            True if scan exists, False otherwise
        """
        return DjangoScan.objects.filter(id=scan_id).exists()
    
    def get_recent_scans(self, user_id: int, limit: int = 10) -> List[Scan]:
        """
        Get recent scans for a user using Django ORM.
        
        Args:
            user_id: User identifier
            limit: Maximum number of scans to return
            
        Returns:
            List of recent scan entities
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            django_scans = DjangoScan.objects.filter(user=django_user).order_by('-scanned_at')[:limit]
            return [self._to_domain_entity(scan) for scan in django_scans]
        except DjangoUser.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found")
            return []
        except Exception as e:
            logger.error(f"Error retrieving recent scans for user {user_id}: {str(e)}")
            raise ScanNotFoundError(f"Error retrieving recent scans for user {user_id}: {str(e)}")
    
    def get_scans_by_type(self, user_id: int, scan_type: str) -> List[Scan]:
        """
        Get scans by type for a user using Django ORM.
        
        Args:
            user_id: User identifier
            scan_type: Type of scan (barcode, image, manual)
            
        Returns:
            List of scan entities with specified type
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            django_scans = DjangoScan.objects.filter(user=django_user, scan_type=scan_type).order_by('-scanned_at')
            return [self._to_domain_entity(scan) for scan in django_scans]
        except DjangoUser.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found")
            return []
        except Exception as e:
            logger.error(f"Error retrieving scans by type {scan_type} for user {user_id}: {str(e)}")
            raise ScanNotFoundError(f"Error retrieving scans by type {scan_type} for user {user_id}: {str(e)}")
    
    def get_scans_with_analysis(self, user_id: int) -> List[Scan]:
        """
        Get scans that have analysis results using Django ORM.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of scan entities with analysis available
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            django_scans = DjangoScan.objects.filter(user=django_user, analysis_available=True).order_by('-scanned_at')
            return [self._to_domain_entity(scan) for scan in django_scans]
        except DjangoUser.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found")
            return []
        except Exception as e:
            logger.error(f"Error retrieving scans with analysis for user {user_id}: {str(e)}")
            raise ScanNotFoundError(f"Error retrieving scans with analysis for user {user_id}: {str(e)}")
    
    def get_scans_by_date_range(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Scan]:
        """
        Get scans within a date range using Django ORM.
        
        Args:
            user_id: User identifier
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of scan entities within date range
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            django_scans = DjangoScan.objects.filter(
                user=django_user,
                scanned_at__gte=start_date,
                scanned_at__lte=end_date
            ).order_by('-scanned_at')
            return [self._to_domain_entity(scan) for scan in django_scans]
        except DjangoUser.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found")
            return []
        except Exception as e:
            logger.error(f"Error retrieving scans by date range for user {user_id}: {str(e)}")
            raise ScanNotFoundError(f"Error retrieving scans by date range for user {user_id}: {str(e)}")
    
    def count_by_user(self, user_id: int) -> int:
        """
        Count total scans for a user using Django ORM.
        
        Args:
            user_id: User identifier
            
        Returns:
            Total number of scans for the user
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            return DjangoScan.objects.filter(user=django_user).count()
        except DjangoUser.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found")
            return 0
        except Exception as e:
            logger.error(f"Error counting scans for user {user_id}: {str(e)}")
            raise ScanNotFoundError(f"Error counting scans for user {user_id}: {str(e)}")
    
    def _to_domain_entity(self, django_scan: DjangoScan) -> Scan:
        """
        Convert Django Scan model to domain entity.
        
        Args:
            django_scan: Django Scan model instance
            
        Returns:
            Scan domain entity
        """
        # Convert Django User to domain User
        user = User(
            user_id=django_scan.user.id,
            username=django_scan.user.username,
            email=django_scan.user.email,
            first_name=django_scan.user.first_name,
            last_name=django_scan.user.last_name,
            is_active=django_scan.user.is_active,
            is_staff=django_scan.user.is_staff,
            is_superuser=django_scan.user.is_superuser
        )
        
        # Create SafetyScore if product_score exists
        safety_score = None
        if django_scan.product_score is not None:
            safety_score = SafetyScore(django_scan.product_score)
        
        # Create Scan domain entity
        return Scan(
            scan_id=django_scan.id,
            user=user,
            scan_type=django_scan.scan_type,
            barcode=django_scan.barcode,
            image_path=django_scan.image.url if django_scan.image else None,
            scanned_at=django_scan.scanned_at,
            notes=django_scan.notes,
            product_name=django_scan.product_name,
            product_brand=django_scan.product_brand,
            product_description=django_scan.product_description,
            product_ingredients_text=django_scan.product_ingredients_text,
            safety_score=safety_score,
            analysis_available=django_scan.analysis_available
        )
    
    def _update_django_scan(self, django_scan: DjangoScan, scan: Scan) -> None:
        """
        Update Django scan model with domain entity data.
        
        Args:
            django_scan: Django Scan model instance
            scan: Scan domain entity
        """
        django_scan.scan_type = scan.scan_type
        django_scan.barcode = scan.barcode
        django_scan.image = scan.image_path
        django_scan.scanned_at = scan.scanned_at
        django_scan.notes = scan.notes
        django_scan.product_name = scan.product_name
        django_scan.product_brand = scan.product_brand
        django_scan.product_description = scan.product_description
        django_scan.product_ingredients_text = scan.product_ingredients_text
        django_scan.product_score = scan.safety_score.score if scan.safety_score else None
        django_scan.product_risk_level = scan.safety_score.risk_level if scan.safety_score else ''
        django_scan.analysis_available = scan.analysis_available
