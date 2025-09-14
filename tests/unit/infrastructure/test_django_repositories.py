"""
Unit tests for Django repositories.

Tests the Django repository implementations with database interactions.
"""

import unittest
from django.test import TestCase
from django.contrib.auth.models import User as DjangoUser
from apps.accounts.models import UserProfile as DjangoUserProfile
from apps.scans.models import Scan as DjangoScan
from infrastructure.repositories.django_user_repository import DjangoUserRepository
from infrastructure.repositories.django_profile_repository import DjangoProfileRepository
from infrastructure.repositories.django_scan_repository import DjangoScanRepository
from core.entities.user import User
from core.entities.profile import UserProfile
from core.entities.scan import Scan
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.value_objects.safety_score import SafetyScore
from core.exceptions import UserNotFoundError, ProfileNotFoundError, ScanNotFoundError


class TestDjangoUserRepository(TestCase):
    """Test cases for DjangoUserRepository."""

    def setUp(self):
        """Set up test data."""
        self.repository = DjangoUserRepository()
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_active=True,
            is_staff=False,
            is_superuser=False
        )

    def test_get_by_id_success(self):
        """Test successful user retrieval by ID."""
        result = self.repository.get_by_id(self.django_user.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.django_user.id)
        self.assertEqual(result.username, 'testuser')
        self.assertEqual(result.email, 'test@example.com')
        self.assertEqual(result.first_name, 'Test')
        self.assertEqual(result.last_name, 'User')
        self.assertTrue(result.is_active)
        self.assertFalse(result.is_staff)
        self.assertFalse(result.is_superuser)

    def test_get_by_id_not_found(self):
        """Test user retrieval when user doesn't exist."""
        result = self.repository.get_by_id(99999)
        self.assertIsNone(result)

    def test_get_by_username_success(self):
        """Test successful user retrieval by username."""
        result = self.repository.get_by_username('testuser')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.username, 'testuser')
        self.assertEqual(result.email, 'test@example.com')

    def test_get_by_username_not_found(self):
        """Test user retrieval when username doesn't exist."""
        result = self.repository.get_by_username('nonexistent')
        self.assertIsNone(result)

    def test_get_by_email_success(self):
        """Test successful user retrieval by email."""
        result = self.repository.get_by_email('test@example.com')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.email, 'test@example.com')
        self.assertEqual(result.username, 'testuser')

    def test_get_by_email_not_found(self):
        """Test user retrieval when email doesn't exist."""
        result = self.repository.get_by_email('nonexistent@example.com')
        self.assertIsNone(result)

    def test_exists_true(self):
        """Test user exists check when user exists."""
        result = self.repository.exists(self.django_user.id)
        self.assertTrue(result)

    def test_exists_false(self):
        """Test user exists check when user doesn't exist."""
        result = self.repository.exists(99999)
        self.assertFalse(result)

    def test_get_all_active_users(self):
        """Test retrieving all active users."""
        # Create another user
        DjangoUser.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        result = self.repository.get_all_active_users()
        
        self.assertEqual(len(result), 2)
        self.assertTrue(all(user.is_active for user in result))


class TestDjangoProfileRepository(TestCase):
    """Test cases for DjangoProfileRepository."""

    def setUp(self):
        """Set up test data."""
        self.repository = DjangoProfileRepository()
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.django_profile = self.django_user.profile
        self.django_profile.skin_type = 'combination'
        self.django_profile.age_range = '26-35'
        self.django_profile.set_skin_concerns_list(['acne', 'aging'])
        self.django_profile.set_allergies_list(['paraben'])
        self.django_profile.allergies_other = 'fragrance'
        self.django_profile.save()

    def test_get_by_user_id_success(self):
        """Test successful profile retrieval by user ID."""
        result = self.repository.get_by_user_id(self.django_user.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.user.id, self.django_user.id)
        self.assertEqual(result.skin_type, SkinType.COMBINATION)
        self.assertEqual(result.age_range, AgeRange.ADULT)
        self.assertEqual(result.skin_concerns, ['acne', 'aging'])
        self.assertEqual(result.allergies, ['paraben'])

    def test_get_by_user_id_not_found(self):
        """Test profile retrieval when user doesn't exist."""
        result = self.repository.get_by_user_id(99999)
        self.assertIsNone(result)

    def test_get_by_user_success(self):
        """Test successful profile retrieval by user entity."""
        user = User(
            user_id=self.django_user.id,
            username=self.django_user.username,
            email=self.django_user.email
        )
        
        result = self.repository.get_by_user(user)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.user.id, self.django_user.id)
        self.assertEqual(result.skin_type, SkinType.COMBINATION)

    def test_exists_true(self):
        """Test profile exists check when profile exists."""
        result = self.repository.exists(self.django_user.id)
        self.assertTrue(result)

    def test_exists_false(self):
        """Test profile exists check when profile doesn't exist."""
        result = self.repository.exists(99999)
        self.assertFalse(result)

    def test_get_users_by_skin_type(self):
        """Test retrieving users by skin type."""
        result = self.repository.get_users_by_skin_type('combination')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].skin_type, SkinType.COMBINATION)

    def test_get_users_by_age_range(self):
        """Test retrieving users by age range."""
        result = self.repository.get_users_by_age_range('26-35')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].age_range, AgeRange.ADULT)

    def test_get_premium_users(self):
        """Test retrieving premium users."""
        self.django_profile.subscription_type = 'premium'
        self.django_profile.save()
        
        result = self.repository.get_premium_users()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].subscription_type, 'premium')


class TestDjangoScanRepository(TestCase):
    """Test cases for DjangoScanRepository."""

    def setUp(self):
        """Set up test data."""
        self.repository = DjangoScanRepository()
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.django_scan = DjangoScan.objects.create(
            user=self.django_user,
            scan_type='barcode',
            barcode='123456789',
            product_name='Test Product',
            product_brand='Test Brand',
            product_score=85.5,
            product_risk_level='low',
            analysis_available=True
        )

    def test_get_by_id_success(self):
        """Test successful scan retrieval by ID."""
        result = self.repository.get_by_id(self.django_scan.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, self.django_scan.id)
        self.assertEqual(result.scan_type, 'barcode')
        self.assertEqual(result.barcode, '123456789')
        self.assertEqual(result.product_name, 'Test Product')
        self.assertEqual(result.product_brand, 'Test Brand')
        self.assertEqual(result.safety_score.score, 85.5)
        self.assertEqual(result.safety_score.risk_level.value, 'low')
        self.assertTrue(result.analysis_available)

    def test_get_by_id_not_found(self):
        """Test scan retrieval when scan doesn't exist."""
        result = self.repository.get_by_id(99999)
        self.assertIsNone(result)

    def test_get_by_user_id_success(self):
        """Test successful scan retrieval by user ID."""
        result = self.repository.get_by_user_id(self.django_user.id)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, self.django_scan.id)
        self.assertEqual(result[0].scan_type, 'barcode')

    def test_get_by_user_id_not_found(self):
        """Test scan retrieval when user doesn't exist."""
        result = self.repository.get_by_user_id(99999)
        self.assertEqual(len(result), 0)

    def test_exists_true(self):
        """Test scan exists check when scan exists."""
        result = self.repository.exists(self.django_scan.id)
        self.assertTrue(result)

    def test_exists_false(self):
        """Test scan exists check when scan doesn't exist."""
        result = self.repository.exists(99999)
        self.assertFalse(result)

    def test_get_scans_by_type(self):
        """Test retrieving scans by type."""
        result = self.repository.get_scans_by_type('barcode')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].scan_type, 'barcode')

    def test_get_scans_with_analysis(self):
        """Test retrieving scans with analysis."""
        result = self.repository.get_scans_with_analysis()
        
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].analysis_available)

    def test_count_by_user(self):
        """Test counting scans for a user."""
        result = self.repository.count_by_user(self.django_user.id)
        self.assertEqual(result, 1)

    def test_save_new_scan(self):
        """Test saving a new scan."""
        user = User(
            user_id=self.django_user.id,
            username=self.django_user.username,
            email=self.django_user.email
        )
        
        safety_score = SafetyScore(75.0)
        new_scan = Scan(
            scan_id=None,
            user=user,
            scan_type='image',
            barcode=None,
            image_path='/media/scans/new_scan.jpg',
            scanned_at=None,
            notes='New scan',
            product_name='New Product',
            product_brand='New Brand',
            product_description='A new product',
            product_ingredients_text='Water, Glycerin',
            safety_score=safety_score,
            analysis_available=True
        )
        
        result = self.repository.save(new_scan)
        
        self.assertIsNotNone(result.id)
        self.assertEqual(result.scan_type, 'image')
        self.assertEqual(result.product_name, 'New Product')
        self.assertEqual(result.safety_score.score, 75.0)

    def test_save_existing_scan(self):
        """Test saving an existing scan."""
        user = User(
            user_id=self.django_user.id,
            username=self.django_user.username,
            email=self.django_user.email
        )
        
        safety_score = SafetyScore(90.0)
        existing_scan = Scan(
            scan_id=self.django_scan.id,
            user=user,
            scan_type='barcode',
            barcode='123456789',
            image_path=None,
            scanned_at=None,
            notes='Updated scan',
            product_name='Updated Product',
            product_brand='Updated Brand',
            product_description='An updated product',
            product_ingredients_text='Water, Glycerin, Paraben',
            safety_score=safety_score,
            analysis_available=True
        )
        
        result = self.repository.save(existing_scan)
        
        self.assertEqual(result.id, self.django_scan.id)
        self.assertEqual(result.product_name, 'Updated Product')
        self.assertEqual(result.safety_score.score, 90.0)


if __name__ == '__main__':
    unittest.main()
