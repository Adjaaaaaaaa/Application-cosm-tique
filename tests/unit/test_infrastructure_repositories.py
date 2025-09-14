"""
Unit tests for infrastructure repositories.

Tests the concrete repository implementations using Django ORM.
"""

import unittest
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User as DjangoUser
from apps.accounts.models import UserProfile as DjangoUserProfile
from apps.scans.models import Scan as DjangoScan

from core.entities.user import User
from core.entities.profile import UserProfile
from core.entities.scan import Scan
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.value_objects.safety_score import SafetyScore

from infrastructure.repositories.django_user_repository import DjangoUserRepository
from infrastructure.repositories.django_profile_repository import DjangoProfileRepository
from infrastructure.repositories.django_scan_repository import DjangoScanRepository


class TestDjangoUserRepository(TestCase):
    """Test DjangoUserRepository."""
    
    def setUp(self):
        """Set up test data."""
        self.repository = DjangoUserRepository()
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
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
        # Create another active user
        DjangoUser.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create inactive user
        DjangoUser.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='testpass123',
            is_active=False
        )
        
        result = self.repository.get_all_active_users()
        
        self.assertEqual(len(result), 2)
        usernames = [user.username for user in result]
        self.assertIn('testuser', usernames)
        self.assertIn('testuser2', usernames)
        self.assertNotIn('inactiveuser', usernames)


class TestDjangoProfileRepository(TestCase):
    """Test DjangoProfileRepository."""
    
    def setUp(self):
        """Set up test data."""
        self.repository = DjangoProfileRepository()
        self.django_user = DjangoUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # UserProfile is created automatically by signal
        self.django_profile = self.django_user.profile
        self.django_profile.skin_type = 'combination'
        self.django_profile.age_range = '26-35'
        self.django_profile.set_allergies_list(['paraben'])
        self.django_profile.allergies_other = 'fragrance'
        self.django_profile.save()
    
    def test_get_by_user_id_success(self):
        """Test successful profile retrieval by user ID."""
        result = self.repository.get_by_user_id(self.django_user.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.user.id, self.django_user.id)
        self.assertEqual(result.skin_type, 'combination')
        self.assertEqual(result.age_range, '26-35')
        self.assertIn('paraben', result.allergies)
        self.assertEqual(result.allergies_other, 'fragrance')
    
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
        self.assertEqual(result.skin_type, 'combination')
    
    def test_exists_true(self):
        """Test profile exists check when profile exists."""
        result = self.repository.exists(self.django_user.id)
        self.assertTrue(result)
    
    def test_exists_false(self):
        """Test profile exists check when user doesn't exist."""
        result = self.repository.exists(99999)
        self.assertFalse(result)
    
    def test_get_premium_users(self):
        """Test retrieving premium users."""
        # Create premium user
        premium_user = DjangoUser.objects.create_user(
            username='premiumuser',
            email='premium@example.com',
            password='testpass123'
        )
        premium_profile = premium_user.profile
        premium_profile.subscription_type = 'premium'
        premium_profile.save()
        
        result = self.repository.get_premium_users()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].subscription_type, 'premium')
        self.assertEqual(result[0].user.username, 'premiumuser')
    
    def test_get_users_by_skin_type(self):
        """Test retrieving users by skin type."""
        result = self.repository.get_users_by_skin_type('combination')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].skin_type, 'combination')
        self.assertEqual(result[0].user.username, 'testuser')
    
    def test_get_users_by_age_range(self):
        """Test retrieving users by age range."""
        result = self.repository.get_users_by_age_range('26-35')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].age_range, '26-35')
        self.assertEqual(result[0].user.username, 'testuser')


class TestDjangoScanRepository(TestCase):
    """Test DjangoScanRepository."""
    
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
            product_risk_level='Low',
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
        self.assertEqual(result[0].user.id, self.django_user.id)
    
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
    
    def test_count_by_user(self):
        """Test counting scans for a user."""
        # Create another scan
        DjangoScan.objects.create(
            user=self.django_user,
            scan_type='image',
            product_name='Another Product'
        )
        
        result = self.repository.count_by_user(self.django_user.id)
        self.assertEqual(result, 2)
    
    def test_get_scans_by_type(self):
        """Test retrieving scans by type."""
        # Create another scan with different type
        DjangoScan.objects.create(
            user=self.django_user,
            scan_type='image',
            product_name='Image Product'
        )
        
        result = self.repository.get_scans_by_type(self.django_user.id, 'barcode')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].scan_type, 'barcode')
        self.assertEqual(result[0].product_name, 'Test Product')
    
    def test_get_scans_with_analysis(self):
        """Test retrieving scans with analysis."""
        # Create scan without analysis
        DjangoScan.objects.create(
            user=self.django_user,
            scan_type='manual',
            product_name='Manual Product',
            analysis_available=False
        )
        
        result = self.repository.get_scans_with_analysis(self.django_user.id)
        
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].analysis_available)
        self.assertEqual(result[0].product_name, 'Test Product')


if __name__ == '__main__':
    unittest.main()
