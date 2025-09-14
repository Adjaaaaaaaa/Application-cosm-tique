"""
Unit tests for UserProfile domain entity.

Tests the UserProfile entity validation, properties, and business logic.
"""

import unittest
from core.entities.user import User
from core.entities.profile import UserProfile
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.exceptions import InvalidInputException


class TestUserProfileEntity(unittest.TestCase):
    """Test cases for UserProfile domain entity."""

    def setUp(self):
        """Set up test data."""
        self.user = User(
            user_id=1,
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        self.valid_profile_data = {
            'user': self.user,
            'subscription_type': 'free',
            'skin_type': SkinType.COMBINATION,
            'age_range': AgeRange.ADULT,
            'skin_concerns': ['acne', 'aging'],
            'dermatological_conditions': ['eczema'],
            'dermatological_other': 'psoriasis',
            'allergies': ['paraben', 'sulfate'],
            'allergies_other': 'fragrance',
            'product_style': 'pharmacy',
            'routine_frequency': 'standard',
            'objectives': ['anti-aging', 'hydration'],
            'budget': 'moderate'
        }

    def test_create_profile_with_valid_data(self):
        """Test creating profile with valid data."""
        profile = UserProfile(**self.valid_profile_data)
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.subscription_type, 'free')
        self.assertEqual(profile.skin_type, SkinType.COMBINATION)
        self.assertEqual(profile.age_range, AgeRange.ADULT)
        self.assertEqual(profile.skin_concerns, ['acne', 'aging'])
        self.assertEqual(profile.dermatological_conditions, ['eczema'])
        self.assertEqual(profile.dermatological_other, 'psoriasis')
        self.assertEqual(profile.allergies, ['paraben', 'sulfate'])
        self.assertEqual(profile.allergies_other, 'fragrance')
        self.assertEqual(profile.product_style, 'pharmacy')
        self.assertEqual(profile.routine_frequency, 'standard')
        self.assertEqual(profile.objectives, ['anti-aging', 'hydration'])
        self.assertEqual(profile.budget, 'moderate')

    def test_create_profile_with_minimal_data(self):
        """Test creating profile with minimal required data."""
        minimal_data = {
            'user': self.user,
            'subscription_type': 'free',
            'skin_type': SkinType.NORMAL,
            'age_range': AgeRange.ADULT
        }
        profile = UserProfile(**minimal_data)
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.subscription_type, 'free')
        self.assertEqual(profile.skin_type, SkinType.NORMAL)
        self.assertEqual(profile.age_range, AgeRange.ADULT)
        self.assertEqual(profile.skin_concerns, [])
        self.assertEqual(profile.dermatological_conditions, [])
        self.assertEqual(profile.dermatological_other, '')
        self.assertEqual(profile.allergies, [])
        self.assertEqual(profile.allergies_other, '')
        self.assertEqual(profile.product_style, '')
        self.assertEqual(profile.routine_frequency, '')
        self.assertEqual(profile.objectives, [])
        self.assertEqual(profile.budget, '')

    def test_create_profile_with_invalid_user(self):
        """Test creating profile with invalid user raises exception."""
        invalid_data = self.valid_profile_data.copy()
        invalid_data['user'] = None
        
        with self.assertRaises(InvalidInputException):
            UserProfile(**invalid_data)

    def test_is_premium_user(self):
        """Test premium user detection."""
        premium_data = self.valid_profile_data.copy()
        premium_data['subscription_type'] = 'premium'
        profile = UserProfile(**premium_data)
        
        self.assertTrue(profile.is_premium_user())

    def test_is_not_premium_user(self):
        """Test non-premium user detection."""
        profile = UserProfile(**self.valid_profile_data)
        self.assertFalse(profile.is_premium_user())

    def test_get_all_allergies(self):
        """Test getting all allergies including other allergies."""
        profile = UserProfile(**self.valid_profile_data)
        all_allergies = profile.get_all_allergies()
        
        expected = ['paraben', 'sulfate', 'fragrance']
        self.assertEqual(all_allergies, expected)

    def test_get_all_allergies_without_other(self):
        """Test getting all allergies without other allergies."""
        data = self.valid_profile_data.copy()
        data['allergies_other'] = ''
        profile = UserProfile(**data)
        all_allergies = profile.get_all_allergies()
        
        expected = ['paraben', 'sulfate']
        self.assertEqual(all_allergies, expected)

    def test_add_allergy(self):
        """Test adding an allergy."""
        profile = UserProfile(**self.valid_profile_data)
        profile.add_allergy('alcohol')
        
        self.assertIn('alcohol', profile.allergies)

    def test_add_duplicate_allergy(self):
        """Test adding duplicate allergy doesn't create duplicates."""
        profile = UserProfile(**self.valid_profile_data)
        initial_count = len(profile.allergies)
        profile.add_allergy('paraben')
        
        self.assertEqual(len(profile.allergies), initial_count)

    def test_remove_allergy(self):
        """Test removing an allergy."""
        profile = UserProfile(**self.valid_profile_data)
        profile.remove_allergy('paraben')
        
        self.assertNotIn('paraben', profile.allergies)

    def test_remove_nonexistent_allergy(self):
        """Test removing non-existent allergy doesn't raise error."""
        profile = UserProfile(**self.valid_profile_data)
        initial_count = len(profile.allergies)
        profile.remove_allergy('nonexistent')
        
        self.assertEqual(len(profile.allergies), initial_count)

    def test_format_for_ai(self):
        """Test formatting profile for AI prompts."""
        profile = UserProfile(**self.valid_profile_data)
        formatted = profile.format_for_ai()
        
        # Check that key information is included
        self.assertIn('testuser', formatted)
        self.assertIn('Mixte', formatted)  # Display name for combination
        self.assertIn('26–35 ans', formatted)  # Display name for adult
        self.assertIn('🚨', formatted)  # Allergy warning emoji
        self.assertIn('⚠️', formatted)  # Condition warning emoji
        self.assertIn('paraben', formatted)
        self.assertIn('fragrance', formatted)
        self.assertIn('eczema', formatted)
        self.assertIn('anti-aging', formatted)

    def test_format_for_ai_with_minimal_data(self):
        """Test formatting profile for AI with minimal data."""
        minimal_data = {
            'user': self.user,
            'subscription_type': 'free',
            'skin_type': SkinType.NORMAL,
            'age_range': AgeRange.ADULT
        }
        profile = UserProfile(**minimal_data)
        formatted = profile.format_for_ai()
        
        self.assertIn('testuser', formatted)
        self.assertIn('Normal', formatted)
        self.assertIn('26–35 ans', formatted)

    def test_to_dict(self):
        """Test converting profile to dictionary."""
        profile = UserProfile(**self.valid_profile_data)
        profile_dict = profile.to_dict()
        
        self.assertEqual(profile_dict['user_id'], 1)
        self.assertEqual(profile_dict['username'], 'testuser')
        self.assertEqual(profile_dict['email'], 'test@example.com')
        self.assertEqual(profile_dict['first_name'], 'Test')
        self.assertEqual(profile_dict['last_name'], 'User')
        self.assertEqual(profile_dict['skin_type'], 'combination')
        self.assertEqual(profile_dict['age_range'], '26-35')
        self.assertEqual(profile_dict['skin_concerns'], ['acne', 'aging'])
        self.assertEqual(profile_dict['dermatological_conditions'], ['eczema'])
        self.assertEqual(profile_dict['dermatological_other'], 'psoriasis')
        self.assertEqual(profile_dict['allergies'], ['paraben', 'sulfate'])
        self.assertEqual(profile_dict['allergies_other'], 'fragrance')
        self.assertEqual(profile_dict['product_style'], 'pharmacy')
        self.assertEqual(profile_dict['routine_frequency'], 'standard')
        self.assertEqual(profile_dict['objectives'], ['anti-aging', 'hydration'])
        self.assertEqual(profile_dict['budget'], 'moderate')
        self.assertEqual(profile_dict['subscription_type'], 'free')

    def test_profile_equality(self):
        """Test profile equality based on user."""
        profile1 = UserProfile(**self.valid_profile_data)
        profile2_data = self.valid_profile_data.copy()
        profile2_data['skin_type'] = SkinType.DRY
        profile2 = UserProfile(**profile2_data)
        
        self.assertEqual(profile1, profile2)

    def test_profile_inequality(self):
        """Test profile inequality with different users."""
        user2 = User(
            user_id=2,
            username='testuser2',
            email='test2@example.com'
        )
        profile1 = UserProfile(**self.valid_profile_data)
        profile2_data = self.valid_profile_data.copy()
        profile2_data['user'] = user2
        profile2 = UserProfile(**profile2_data)
        
        self.assertNotEqual(profile1, profile2)

    def test_profile_hash(self):
        """Test profile hash based on user."""
        profile1 = UserProfile(**self.valid_profile_data)
        profile2_data = self.valid_profile_data.copy()
        profile2_data['skin_type'] = SkinType.DRY
        profile2 = UserProfile(**profile2_data)
        
        self.assertEqual(hash(profile1), hash(profile2))

    def test_profile_string_representation(self):
        """Test profile string representation."""
        profile = UserProfile(**self.valid_profile_data)
        expected = "UserProfile(user=User(id=1, username='testuser'))"
        self.assertEqual(str(profile), expected)

    def test_profile_repr(self):
        """Test profile detailed string representation."""
        profile = UserProfile(**self.valid_profile_data)
        repr_str = repr(profile)
        self.assertIn('UserProfile(', repr_str)
        self.assertIn("user=User(user_id=1", repr_str)
        self.assertIn("skin_type=SkinType.COMBINATION", repr_str)


if __name__ == '__main__':
    unittest.main()
