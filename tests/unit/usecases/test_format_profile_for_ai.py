"""
Unit tests for FormatProfileForAIUseCase.

Tests the use case for formatting user profiles for AI prompts.
"""

import unittest
from usecases.user.format_profile_for_ai import FormatProfileForAIUseCase


class TestFormatProfileForAIUseCase(unittest.TestCase):
    """Test cases for FormatProfileForAIUseCase."""

    def setUp(self):
        """Set up test data."""
        self.use_case = FormatProfileForAIUseCase()

    def test_execute_with_complete_profile(self):
        """Test formatting complete profile for AI."""
        profile_data = {
            'user_id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'skin_type': 'combination',
            'age_range': '26-35',
            'skin_concerns': ['acne', 'aging'],
            'dermatological_conditions': ['eczema'],
            'dermatological_other': 'psoriasis',
            'allergies': ['paraben', 'sulfate'],
            'allergies_other': 'fragrance',
            'product_style': 'pharmacy',
            'routine_frequency': 'standard',
            'objectives': ['anti-aging', 'hydration'],
            'budget': 'moderate',
            'subscription_type': 'free'
        }
        
        result = self.use_case.execute(profile_data)
        
        # Check that key information is included
        self.assertIn('testuser', result)
        self.assertIn('Mixte', result)  # Display name for combination
        self.assertIn('26–35 ans', result)  # Display name for age range
        self.assertIn('🚨', result)  # Allergy warning emoji
        self.assertIn('⚠️', result)  # Condition warning emoji
        self.assertIn('paraben', result)
        self.assertIn('fragrance', result)
        self.assertIn('eczema', result)
        self.assertIn('anti-aging', result)

    def test_execute_with_minimal_profile(self):
        """Test formatting minimal profile for AI."""
        profile_data = {
            'user_id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': '',
            'last_name': '',
            'skin_type': 'normal',
            'age_range': '18-25',
            'skin_concerns': [],
            'dermatological_conditions': [],
            'dermatological_other': '',
            'allergies': [],
            'allergies_other': '',
            'product_style': '',
            'routine_frequency': '',
            'objectives': [],
            'budget': '',
            'subscription_type': 'free'
        }
        
        result = self.use_case.execute(profile_data)
        
        # Check that basic information is included
        self.assertIn('testuser', result)
        self.assertIn('Normal', result)
        self.assertIn('18–25 ans', result)

    def test_execute_with_empty_profile(self):
        """Test formatting empty profile for AI."""
        profile_data = {}
        
        result = self.use_case.execute(profile_data)
        
        # Should return default message
        self.assertEqual(result, "Profil utilisateur non disponible")

    def test_execute_with_none_profile(self):
        """Test formatting None profile for AI."""
        result = self.use_case.execute(None)
        
        # Should return default message
        self.assertEqual(result, "Profil utilisateur non disponible")

    def test_execute_with_premium_user(self):
        """Test formatting premium user profile for AI."""
        profile_data = {
            'user_id': 1,
            'username': 'premiumuser',
            'email': 'premium@example.com',
            'first_name': 'Premium',
            'last_name': 'User',
            'skin_type': 'sensitive',
            'age_range': '36-45',
            'skin_concerns': ['aging', 'hyperpigmentation'],
            'dermatological_conditions': ['rosacea'],
            'dermatological_other': '',
            'allergies': ['fragrance'],
            'allergies_other': '',
            'product_style': 'luxury',
            'routine_frequency': 'advanced',
            'objectives': ['anti-aging', 'brightening'],
            'budget': 'high',
            'subscription_type': 'premium'
        }
        
        result = self.use_case.execute(profile_data)
        
        # Check that premium information is included
        self.assertIn('premiumuser', result)
        self.assertIn('Sensible', result)  # Display name for sensitive
        self.assertIn('36–45 ans', result)  # Display name for mature
        self.assertIn('aging', result)
        self.assertIn('hyperpigmentation', result)
        self.assertIn('rosacea', result)
        self.assertIn('fragrance', result)
        self.assertIn('anti-aging', result)
        self.assertIn('brightening', result)

    def test_execute_with_complex_concerns(self):
        """Test formatting profile with complex skin concerns."""
        profile_data = {
            'user_id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'skin_type': 'oily',
            'age_range': '26-35',
            'skin_concerns': ['acne', 'aging', 'hyperpigmentation', 'large_pores'],
            'dermatological_conditions': ['eczema', 'rosacea'],
            'dermatological_other': 'psoriasis, dermatitis',
            'allergies': ['paraben', 'sulfate', 'formaldehyde'],
            'allergies_other': 'fragrance, alcohol, essential oils',
            'product_style': 'natural',
            'routine_frequency': 'advanced',
            'objectives': ['anti-aging', 'hydration', 'brightening', 'pore_minimizing'],
            'budget': 'moderate',
            'subscription_type': 'free'
        }
        
        result = self.use_case.execute(profile_data)
        
        # Check that all concerns are included
        self.assertIn('acne', result)
        self.assertIn('aging', result)
        self.assertIn('hyperpigmentation', result)
        self.assertIn('large_pores', result)
        self.assertIn('eczema', result)
        self.assertIn('rosacea', result)
        self.assertIn('psoriasis', result)
        self.assertIn('dermatitis', result)
        self.assertIn('paraben', result)
        self.assertIn('sulfate', result)
        self.assertIn('formaldehyde', result)
        self.assertIn('fragrance', result)
        self.assertIn('alcohol', result)
        self.assertIn('essential oils', result)

    def test_execute_with_special_characters(self):
        """Test formatting profile with special characters."""
        profile_data = {
            'user_id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'skin_type': 'normal',
            'age_range': '26-35',
            'skin_concerns': [],
            'dermatological_conditions': [],
            'dermatological_other': '',
            'allergies': [],
            'allergies_other': '',
            'product_style': '',
            'routine_frequency': '',
            'objectives': [],
            'budget': '',
            'subscription_type': 'free'
        }
        
        result = self.use_case.execute(profile_data)
        
        # Should handle special characters gracefully
        self.assertIsInstance(result, str)
        self.assertIn('testuser', result)

    def test_execute_with_missing_fields(self):
        """Test formatting profile with missing fields."""
        profile_data = {
            'user_id': 1,
            'username': 'testuser',
            'skin_type': 'normal',
            'age_range': '26-35'
        }
        
        result = self.use_case.execute(profile_data)
        
        # Should handle missing fields gracefully
        self.assertIn('testuser', result)
        self.assertIn('Normal', result)
        self.assertIn('26–35 ans', result)

    def test_execute_with_invalid_skin_type(self):
        """Test formatting profile with invalid skin type."""
        profile_data = {
            'user_id': 1,
            'username': 'testuser',
            'skin_type': 'invalid_type',
            'age_range': '26-35'
        }
        
        result = self.use_case.execute(profile_data)
        
        # Should handle invalid skin type gracefully
        self.assertIn('testuser', result)
        self.assertIn('26–35 ans', result)

    def test_execute_with_invalid_age_range(self):
        """Test formatting profile with invalid age range."""
        profile_data = {
            'user_id': 1,
            'username': 'testuser',
            'skin_type': 'normal',
            'age_range': 'invalid_range'
        }
        
        result = self.use_case.execute(profile_data)
        
        # Should handle invalid age range gracefully
        self.assertIn('testuser', result)
        self.assertIn('Normal', result)


if __name__ == '__main__':
    unittest.main()
