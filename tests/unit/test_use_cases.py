"""
Unit tests for use cases.

Tests the application logic in use cases without any framework dependencies.
"""

import unittest
from unittest.mock import Mock, MagicMock

from core.entities.user import User
from core.entities.profile import UserProfile
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.exceptions import UserNotFoundError, ProfileNotFoundError

from usecases.user.get_user_profile import GetUserProfileUseCase
from usecases.user.get_user_allergies import GetUserAllergiesUseCase
from usecases.user.format_profile_for_ai import FormatProfileForAIUseCase


class TestGetUserProfileUseCase(unittest.TestCase):
    """Test GetUserProfileUseCase."""
    
    def setUp(self):
        """Set up test data."""
        self.user_repository = Mock()
        self.profile_repository = Mock()
        self.use_case = GetUserProfileUseCase(
            self.user_repository, 
            self.profile_repository
        )
        
        self.user = User(
            user_id=1,
            username="testuser",
            email="test@example.com"
        )
        
        self.profile = UserProfile(
            user=self.user,
            skin_type=SkinType.COMBINATION,
            age_range=AgeRange.AGE_26_35
        )
    
    def test_execute_success(self):
        """Test successful profile retrieval."""
        self.user_repository.get_by_id.return_value = self.user
        self.profile_repository.get_by_user_id.return_value = self.profile
        
        result = self.use_case.execute(1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['user_id'], 1)
        self.assertEqual(result['username'], 'testuser')
        self.assertEqual(result['skin_type'], 'combination')
        self.assertEqual(result['age_range'], '26-35')
        
        self.user_repository.get_by_id.assert_called_once_with(1)
        self.profile_repository.get_by_user_id.assert_called_once_with(1)
    
    def test_execute_user_not_found(self):
        """Test when user is not found."""
        self.user_repository.get_by_id.return_value = None
        
        with self.assertRaises(UserNotFoundError):
            self.use_case.execute(1)
    
    def test_execute_profile_not_found(self):
        """Test when profile is not found."""
        self.user_repository.get_by_id.return_value = self.user
        self.profile_repository.get_by_user_id.return_value = None
        
        with self.assertRaises(ProfileNotFoundError):
            self.use_case.execute(1)


class TestGetUserAllergiesUseCase(unittest.TestCase):
    """Test GetUserAllergiesUseCase."""
    
    def setUp(self):
        """Set up test data."""
        self.user_repository = Mock()
        self.profile_repository = Mock()
        self.use_case = GetUserAllergiesUseCase(
            self.user_repository, 
            self.profile_repository
        )
        
        self.user = User(
            user_id=1,
            username="testuser",
            email="test@example.com"
        )
        
        self.profile = UserProfile(
            user=self.user,
            allergies=["paraben", "sulfate"],
            allergies_other="fragrance"
        )
    
    def test_execute_success(self):
        """Test successful allergies retrieval."""
        self.user_repository.get_by_id.return_value = self.user
        self.profile_repository.get_by_user_id.return_value = self.profile
        
        result = self.use_case.execute(1)
        
        self.assertEqual(len(result), 3)
        self.assertIn("paraben", result)
        self.assertIn("sulfate", result)
        self.assertIn("fragrance", result)
    
    def test_execute_user_not_found(self):
        """Test when user is not found."""
        self.user_repository.get_by_id.return_value = None
        
        with self.assertRaises(UserNotFoundError):
            self.use_case.execute(1)
    
    def test_execute_profile_not_found(self):
        """Test when profile is not found."""
        self.user_repository.get_by_id.return_value = self.user
        self.profile_repository.get_by_user_id.return_value = None
        
        with self.assertRaises(ProfileNotFoundError):
            self.use_case.execute(1)


class TestFormatProfileForAIUseCase(unittest.TestCase):
    """Test FormatProfileForAIUseCase."""
    
    def setUp(self):
        """Set up test data."""
        self.use_case = FormatProfileForAIUseCase()
    
    def test_execute_success(self):
        """Test successful profile formatting."""
        profile_data = {
            'user_id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'skin_type': 'combination',
            'age_range': '26-35',
            'skin_concerns': ['acne'],
            'allergies': ['paraben'],
            'objectives': ['anti-aging']
        }
        
        result = self.use_case.execute(profile_data)
        
        self.assertIn('testuser', result)
        self.assertIn('Mixte', result)  # Display name for combination
        self.assertIn('26–35 ans', result)  # Display name for age range
        self.assertIn('🚨', result)  # Allergy warning emoji
        self.assertIn('paraben', result)
        self.assertIn('acne', result)
        self.assertIn('anti-aging', result)
    
    def test_execute_empty_profile(self):
        """Test formatting empty profile."""
        result = self.use_case.execute({})
        
        self.assertEqual(result, "Profil utilisateur non disponible")
    
    def test_execute_none_profile(self):
        """Test formatting None profile."""
        result = self.use_case.execute(None)
        
        self.assertEqual(result, "Profil utilisateur non disponible")
    
    def test_execute_with_entities(self):
        """Test formatting with domain entities."""
        user = User(
            user_id=1,
            username="testuser",
            email="test@example.com"
        )
        
        profile = UserProfile(
            user=user,
            skin_type=SkinType.COMBINATION,
            age_range=AgeRange.AGE_26_35,
            allergies=["paraben"]
        )
        
        result = self.use_case.execute_with_entities(profile)
        
        self.assertIn('testuser', result)
        self.assertIn('Mixte', result)
        self.assertIn('🚨', result)
        self.assertIn('paraben', result)


if __name__ == '__main__':
    unittest.main()
