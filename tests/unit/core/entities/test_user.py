"""
Unit tests for User domain entity.

Tests the User entity validation, properties, and business logic.
"""

import unittest
from core.entities.user import User
from core.exceptions import UserNotFoundError


class TestUserEntity(unittest.TestCase):
    """Test cases for User domain entity."""

    def setUp(self):
        """Set up test data."""
        self.valid_user_data = {
            'user_id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
            'is_staff': False,
            'is_superuser': False
        }

    def test_create_user_with_valid_data(self):
        """Test creating user with valid data."""
        user = User(**self.valid_user_data)
        
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_minimal_data(self):
        """Test creating user with minimal required data."""
        minimal_data = {
            'user_id': 2,
            'username': 'minimal',
            'email': 'minimal@example.com'
        }
        user = User(**minimal_data)
        
        self.assertEqual(user.id, 2)
        self.assertEqual(user.username, 'minimal')
        self.assertEqual(user.email, 'minimal@example.com')
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_invalid_id(self):
        """Test creating user with invalid ID raises exception."""
        invalid_data = self.valid_user_data.copy()
        invalid_data['user_id'] = 0
        
        with self.assertRaises(UserNotFoundError):
            User(**invalid_data)

    def test_create_user_with_empty_username(self):
        """Test creating user with empty username raises exception."""
        invalid_data = self.valid_user_data.copy()
        invalid_data['username'] = ''
        
        with self.assertRaises(UserNotFoundError):
            User(**invalid_data)

    def test_create_user_with_empty_email(self):
        """Test creating user with empty email raises exception."""
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = ''
        
        with self.assertRaises(UserNotFoundError):
            User(**invalid_data)

    def test_get_full_name(self):
        """Test getting user's full name."""
        user = User(**self.valid_user_data)
        self.assertEqual(user.get_full_name(), 'Test User')

    def test_get_full_name_with_first_name_only(self):
        """Test getting full name with first name only."""
        data = self.valid_user_data.copy()
        data['last_name'] = ''
        user = User(**data)
        self.assertEqual(user.get_full_name(), 'Test')

    def test_get_full_name_with_last_name_only(self):
        """Test getting full name with last name only."""
        data = self.valid_user_data.copy()
        data['first_name'] = ''
        user = User(**data)
        self.assertEqual(user.get_full_name(), 'User')

    def test_get_full_name_with_no_names(self):
        """Test getting full name with no first or last name."""
        data = self.valid_user_data.copy()
        data['first_name'] = ''
        data['last_name'] = ''
        user = User(**data)
        self.assertEqual(user.get_full_name(), 'testuser')

    def test_get_display_name(self):
        """Test getting user's display name."""
        user = User(**self.valid_user_data)
        self.assertEqual(user.get_display_name(), 'Test User')

    def test_get_display_name_fallback_to_username(self):
        """Test display name falls back to username when no full name."""
        data = self.valid_user_data.copy()
        data['first_name'] = ''
        data['last_name'] = ''
        user = User(**data)
        self.assertEqual(user.get_display_name(), 'testuser')

    def test_user_equality(self):
        """Test user equality based on ID."""
        user1 = User(**self.valid_user_data)
        user2_data = self.valid_user_data.copy()
        user2_data['username'] = 'different'
        user2 = User(**user2_data)
        
        self.assertEqual(user1, user2)

    def test_user_inequality(self):
        """Test user inequality with different IDs."""
        user1 = User(**self.valid_user_data)
        user2_data = self.valid_user_data.copy()
        user2_data['user_id'] = 2
        user2 = User(**user2_data)
        
        self.assertNotEqual(user1, user2)

    def test_user_hash(self):
        """Test user hash based on ID."""
        user1 = User(**self.valid_user_data)
        user2_data = self.valid_user_data.copy()
        user2_data['username'] = 'different'
        user2 = User(**user2_data)
        
        self.assertEqual(hash(user1), hash(user2))

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User(**self.valid_user_data)
        expected = "User(id=1, username='testuser')"
        self.assertEqual(str(user), expected)

    def test_user_repr(self):
        """Test user detailed string representation."""
        user = User(**self.valid_user_data)
        repr_str = repr(user)
        self.assertIn('User(user_id=1', repr_str)
        self.assertIn("username='testuser'", repr_str)
        self.assertIn("email='test@example.com'", repr_str)

    def test_username_whitespace_trimming(self):
        """Test that username whitespace is trimmed."""
        data = self.valid_user_data.copy()
        data['username'] = '  testuser  '
        user = User(**data)
        self.assertEqual(user.username, 'testuser')

    def test_email_whitespace_trimming(self):
        """Test that email whitespace is trimmed."""
        data = self.valid_user_data.copy()
        data['email'] = '  test@example.com  '
        user = User(**data)
        self.assertEqual(user.email, 'test@example.com')

    def test_name_whitespace_trimming(self):
        """Test that first and last names whitespace is trimmed."""
        data = self.valid_user_data.copy()
        data['first_name'] = '  Test  '
        data['last_name'] = '  User  '
        user = User(**data)
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')

    def test_staff_user_properties(self):
        """Test staff user properties."""
        data = self.valid_user_data.copy()
        data['is_staff'] = True
        user = User(**data)
        
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_properties(self):
        """Test superuser properties."""
        data = self.valid_user_data.copy()
        data['is_staff'] = True
        data['is_superuser'] = True
        user = User(**data)
        
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_inactive_user(self):
        """Test inactive user properties."""
        data = self.valid_user_data.copy()
        data['is_active'] = False
        user = User(**data)
        
        self.assertFalse(user.is_active)


if __name__ == '__main__':
    unittest.main()
