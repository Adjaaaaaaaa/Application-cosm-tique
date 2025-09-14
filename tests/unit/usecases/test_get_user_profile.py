"""
Unit tests for GetUserProfileUseCase.

Tests the use case with mocked repositories.
"""

import unittest
from unittest.mock import Mock, patch
from core.entities.user import User
from core.entities.profile import UserProfile
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.exceptions import UserNotFoundError, ProfileNotFoundError
from usecases.user.get_user_profile import GetUserProfileUseCase


class TestGetUserProfileUseCase(unittest.TestCase):
    """Test cases for GetUserProfileUseCase."""

    def setUp(self):
        """Set up test data and mocks."""
        self.mock_user_repository = Mock()
        self.mock_profile_repository = Mock()
        
        self.use_case = GetUserProfileUseCase(
            self.mock_user_repository,
            self.mock_profile_repository
        )
        
        # Create test user
        self.test_user = User(
            user_id=1,
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create test profile
        self.test_profile = UserProfile(
            user=self.test_user,
            subscription_type='free',
            skin_type=SkinType.COMBINATION,
            age_range=AgeRange.ADULT,
            skin_concerns=['acne'],
            dermatological_conditions=[],
            dermatological_other='',
            allergies=['paraben'],
            allergies_other='',
            product_style='pharmacy',
            routine_frequency='standard',
            objectives=['anti-aging'],
            budget='moderate'
        )

    def test_execute_success(self):
        """Test successful profile retrieval."""
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = self.test_profile
        
        # Execute use case
        result = self.use_case.execute(1)
        
        # Verify calls
        self.mock_user_repository.get_by_id.assert_called_once_with(1)
        self.mock_profile_repository.get_by_user_id.assert_called_once_with(1)
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result['user_id'], 1)
        self.assertEqual(result['username'], 'testuser')
        self.assertEqual(result['skin_type'], 'combination')
        self.assertEqual(result['age_range'], '26-35')

    def test_execute_user_not_found(self):
        """Test user not found raises exception."""
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = None
        
        # Execute and verify exception
        with self.assertRaises(UserNotFoundError):
            self.use_case.execute(999)
        
        # Verify calls
        self.mock_user_repository.get_by_id.assert_called_once_with(999)
        self.mock_profile_repository.get_by_user_id.assert_not_called()

    def test_execute_profile_not_found(self):
        """Test profile not found raises exception."""
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = None
        
        # Execute and verify exception
        with self.assertRaises(ProfileNotFoundError):
            self.use_case.execute(1)
        
        # Verify calls
        self.mock_user_repository.get_by_id.assert_called_once_with(1)
        self.mock_profile_repository.get_by_user_id.assert_called_once_with(1)

    def test_execute_with_user_entity_success(self):
        """Test successful profile retrieval returning domain entity."""
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = self.test_profile
        
        # Execute use case
        result = self.use_case.execute_with_user_entity(1)
        
        # Verify calls
        self.mock_user_repository.get_by_id.assert_called_once_with(1)
        self.mock_profile_repository.get_by_user_id.assert_called_once_with(1)
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result, self.test_profile)

    def test_execute_with_user_entity_user_not_found(self):
        """Test user not found returns None for entity method."""
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = None
        
        # Execute use case
        result = self.use_case.execute_with_user_entity(999)
        
        # Verify result
        self.assertIsNone(result)
        
        # Verify calls
        self.mock_user_repository.get_by_id.assert_called_once_with(999)
        self.mock_profile_repository.get_by_user_id.assert_not_called()

    def test_execute_with_user_entity_profile_not_found(self):
        """Test profile not found returns None for entity method."""
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = None
        
        # Execute use case
        result = self.use_case.execute_with_user_entity(1)
        
        # Verify result
        self.assertIsNone(result)
        
        # Verify calls
        self.mock_user_repository.get_by_id.assert_called_once_with(1)
        self.mock_profile_repository.get_by_user_id.assert_called_once_with(1)

    def test_execute_with_premium_user(self):
        """Test profile retrieval for premium user."""
        # Create premium profile
        premium_profile = UserProfile(
            user=self.test_user,
            subscription_type='premium',
            skin_type=SkinType.SENSITIVE,
            age_range=AgeRange.MATURE,
            skin_concerns=['aging'],
            dermatological_conditions=[],
            dermatological_other='',
            allergies=[],
            allergies_other='',
            product_style='luxury',
            routine_frequency='advanced',
            objectives=['anti-aging', 'hydration'],
            budget='high'
        )
        
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = premium_profile
        
        # Execute use case
        result = self.use_case.execute(1)
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(result['subscription_type'], 'premium')
        self.assertEqual(result['skin_type'], 'sensitive')
        self.assertEqual(result['age_range'], '36-45')
        self.assertEqual(result['product_style'], 'luxury')
        self.assertEqual(result['budget'], 'high')

    def test_execute_with_complex_profile(self):
        """Test profile retrieval with complex profile data."""
        # Create complex profile
        complex_profile = UserProfile(
            user=self.test_user,
            subscription_type='free',
            skin_type=SkinType.COMBINATION,
            age_range=AgeRange.ADULT,
            skin_concerns=['acne', 'aging', 'hyperpigmentation'],
            dermatological_conditions=['rosacea', 'eczema'],
            dermatological_other='psoriasis',
            allergies=['paraben', 'sulfate', 'fragrance'],
            allergies_other='alcohol',
            product_style='natural',
            routine_frequency='advanced',
            objectives=['anti-aging', 'hydration', 'brightening'],
            budget='moderate'
        )
        
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = complex_profile
        
        # Execute use case
        result = self.use_case.execute(1)
        
        # Verify result
        self.assertIsNotNone(result)
        self.assertEqual(len(result['skin_concerns']), 3)
        self.assertEqual(len(result['dermatological_conditions']), 2)
        self.assertEqual(len(result['allergies']), 3)
        self.assertEqual(len(result['objectives']), 3)
        self.assertEqual(result['dermatological_other'], 'psoriasis')
        self.assertEqual(result['allergies_other'], 'alcohol')


if __name__ == '__main__':
    unittest.main()
