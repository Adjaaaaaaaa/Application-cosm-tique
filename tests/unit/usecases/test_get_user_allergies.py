"""
Unit tests for GetUserAllergiesUseCase.

Tests the use case with mocked repositories.
"""

import unittest
from unittest.mock import Mock
from core.entities.user import User
from core.entities.profile import UserProfile
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.exceptions import UserNotFoundError, ProfileNotFoundError
from usecases.user.get_user_allergies import GetUserAllergiesUseCase


class TestGetUserAllergiesUseCase(unittest.TestCase):
    """Test cases for GetUserAllergiesUseCase."""

    def setUp(self):
        """Set up test data and mocks."""
        self.mock_user_repository = Mock()
        self.mock_profile_repository = Mock()
        
        self.use_case = GetUserAllergiesUseCase(
            self.mock_user_repository,
            self.mock_profile_repository
        )
        
        # Create test user
        self.test_user = User(
            user_id=1,
            username='testuser',
            email='test@example.com'
        )

    def test_execute_success_with_allergies(self):
        """Test successful allergies retrieval."""
        # Create test profile with allergies
        test_profile = UserProfile(
            user=self.test_user,
            subscription_type='free',
            skin_type=SkinType.NORMAL,
            age_range=AgeRange.ADULT,
            skin_concerns=[],
            dermatological_conditions=[],
            dermatological_other='',
            allergies=['paraben', 'sulfate'],
            allergies_other='fragrance',
            product_style='',
            routine_frequency='',
            objectives=[],
            budget=''
        )
        
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = test_profile
        
        # Execute use case
        result = self.use_case.execute(1)
        
        # Verify calls
        self.mock_user_repository.get_by_id.assert_called_once_with(1)
        self.mock_profile_repository.get_by_user_id.assert_called_once_with(1)
        
        # Verify result
        expected_allergies = ['paraben', 'sulfate', 'fragrance']
        self.assertEqual(result, expected_allergies)

    def test_execute_success_without_allergies(self):
        """Test successful allergies retrieval with no allergies."""
        # Create test profile without allergies
        test_profile = UserProfile(
            user=self.test_user,
            subscription_type='free',
            skin_type=SkinType.NORMAL,
            age_range=AgeRange.ADULT,
            skin_concerns=[],
            dermatological_conditions=[],
            dermatological_other='',
            allergies=[],
            allergies_other='',
            product_style='',
            routine_frequency='',
            objectives=[],
            budget=''
        )
        
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = test_profile
        
        # Execute use case
        result = self.use_case.execute(1)
        
        # Verify result
        self.assertEqual(result, [])

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

    def test_execute_with_only_other_allergies(self):
        """Test allergies retrieval with only other allergies."""
        # Create test profile with only other allergies
        test_profile = UserProfile(
            user=self.test_user,
            subscription_type='free',
            skin_type=SkinType.NORMAL,
            age_range=AgeRange.ADULT,
            skin_concerns=[],
            dermatological_conditions=[],
            dermatological_other='',
            allergies=[],
            allergies_other='alcohol, fragrance',
            product_style='',
            routine_frequency='',
            objectives=[],
            budget=''
        )
        
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = test_profile
        
        # Execute use case
        result = self.use_case.execute(1)
        
        # Verify result
        expected_allergies = ['alcohol', 'fragrance']
        self.assertEqual(result, expected_allergies)

    def test_execute_with_mixed_allergies(self):
        """Test allergies retrieval with mixed allergies."""
        # Create test profile with mixed allergies
        test_profile = UserProfile(
            user=self.test_user,
            subscription_type='free',
            skin_type=SkinType.NORMAL,
            age_range=AgeRange.ADULT,
            skin_concerns=[],
            dermatological_conditions=[],
            dermatological_other='',
            allergies=['paraben', 'sulfate'],
            allergies_other='fragrance, alcohol',
            product_style='',
            routine_frequency='',
            objectives=[],
            budget=''
        )
        
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = test_profile
        
        # Execute use case
        result = self.use_case.execute(1)
        
        # Verify result
        expected_allergies = ['paraben', 'sulfate', 'fragrance', 'alcohol']
        self.assertEqual(result, expected_allergies)

    def test_execute_with_duplicate_allergies(self):
        """Test allergies retrieval with duplicate allergies."""
        # Create test profile with duplicate allergies
        test_profile = UserProfile(
            user=self.test_user,
            subscription_type='free',
            skin_type=SkinType.NORMAL,
            age_range=AgeRange.ADULT,
            skin_concerns=[],
            dermatological_conditions=[],
            dermatological_other='',
            allergies=['paraben'],
            allergies_other='paraben, fragrance',
            product_style='',
            routine_frequency='',
            objectives=[],
            budget=''
        )
        
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = test_profile
        
        # Execute use case
        result = self.use_case.execute(1)
        
        # Verify result (duplicates should be handled by the profile entity)
        expected_allergies = ['paraben', 'fragrance']
        self.assertEqual(result, expected_allergies)

    def test_execute_with_complex_allergies(self):
        """Test allergies retrieval with complex allergy data."""
        # Create test profile with complex allergies
        test_profile = UserProfile(
            user=self.test_user,
            subscription_type='premium',
            skin_type=SkinType.SENSITIVE,
            age_range=AgeRange.MATURE,
            skin_concerns=[],
            dermatological_conditions=[],
            dermatological_other='',
            allergies=['paraben', 'sulfate', 'formaldehyde', 'triclosan'],
            allergies_other='fragrance, alcohol, essential oils',
            product_style='',
            routine_frequency='',
            objectives=[],
            budget=''
        )
        
        # Setup mocks
        self.mock_user_repository.get_by_id.return_value = self.test_user
        self.mock_profile_repository.get_by_user_id.return_value = test_profile
        
        # Execute use case
        result = self.use_case.execute(1)
        
        # Verify result
        expected_allergies = [
            'paraben', 'sulfate', 'formaldehyde', 'triclosan',
            'fragrance', 'alcohol', 'essential oils'
        ]
        self.assertEqual(result, expected_allergies)


if __name__ == '__main__':
    unittest.main()
