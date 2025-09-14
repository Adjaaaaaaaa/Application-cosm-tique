"""
Integration tests for accounts app.

Tests the accounts app endpoints and views to ensure they work correctly
with the Clean Architecture refactoring.
"""

import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.accounts.models import UserProfile


class TestAccountsIntegration(TestCase):
    """Integration tests for accounts app."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        # UserProfile is automatically created by signal
        self.profile = self.user.profile
        self.profile.skin_type = 'combination'
        self.profile.age_range = '26-35'
        self.profile.save()

    def test_home_page_accessible(self):
        """Test that home page is accessible."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BeautyScan')

    def test_login_page_accessible(self):
        """Test that login page is accessible."""
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Connexion')

    def test_signup_page_accessible(self):
        """Test that signup page is accessible."""
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Créer votre compte')

    def test_login_flow(self):
        """Test user login functionality."""
        # Test successful login
        response = self.client.post('/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/login/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'Connexion')

    def test_profile_page_requires_login(self):
        """Test that profile page requires login."""
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_page_accessible_when_logged_in(self):
        """Test that profile page is accessible when logged in."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_profile_update(self):
        """Test profile update functionality."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/profile/', {
            'first_name': 'Updated',
            'last_name': 'Name',
            'skin_type': 'dry',
            'age_range': '18-25'
        })
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        
        # Verify profile was updated
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.profile.skin_type, 'dry')
        self.assertEqual(self.profile.age_range, '18-25')

    def test_signup_flow(self):
        """Test user signup functionality."""
        response = self.client.post('/signup/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        
        # Should redirect after successful signup
        self.assertEqual(response.status_code, 302)
        
        # Verify user was created
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertEqual(new_user.first_name, 'New')
        self.assertEqual(new_user.last_name, 'User')
        
        # Verify profile was created
        self.assertTrue(hasattr(new_user, 'profile'))

    def test_signup_with_existing_email(self):
        """Test signup with existing email fails."""
        response = self.client.post('/signup/', {
            'username': 'anotheruser',
            'email': 'test@example.com',  # Already exists
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        
        # Should stay on signup page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Créer votre compte')

    def test_signup_with_password_mismatch(self):
        """Test signup with password mismatch fails."""
        response = self.client.post('/signup/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass'
        })
        
        # Should stay on signup page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Créer votre compte')

    def test_logout_functionality(self):
        """Test user logout functionality."""
        self.client.login(username='testuser', password='testpass123')
        
        # Verify user is logged in
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        
        # Logout
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        
        # Verify user is logged out
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_with_allergies(self):
        """Test profile with allergies data."""
        # Add allergies to profile
        self.profile.set_allergies_list(['paraben', 'sulfate'])
        self.profile.allergies_other = 'fragrance'
        self.profile.save()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'paraben')
        self.assertContains(response, 'sulfate')
        self.assertContains(response, 'fragrance')

    def test_profile_with_skin_concerns(self):
        """Test profile with skin concerns data."""
        # Add skin concerns to profile
        self.profile.set_skin_concerns_list(['acne', 'aging'])
        self.profile.save()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'acne')
        self.assertContains(response, 'aging')

    def test_profile_with_dermatological_conditions(self):
        """Test profile with dermatological conditions."""
        # Add dermatological conditions to profile
        self.profile.set_dermatological_conditions_list(['eczema'])
        self.profile.dermatological_other = 'psoriasis'
        self.profile.save()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'eczema')
        self.assertContains(response, 'psoriasis')

    def test_profile_with_objectives(self):
        """Test profile with objectives data."""
        # Add objectives to profile
        self.profile.set_objectives_list(['anti-aging', 'hydration'])
        self.profile.save()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'anti-aging')
        self.assertContains(response, 'hydration')

    def test_profile_css_loading(self):
        """Test that profile page loads CSS correctly."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/profile/')
        
        self.assertEqual(response.status_code, 200)
        # Check that CSS file is referenced
        self.assertContains(response, 'profile.css')

    def test_signup_css_loading(self):
        """Test that signup page loads CSS correctly."""
        response = self.client.get('/signup/')
        
        self.assertEqual(response.status_code, 200)
        # Check that CSS file is referenced
        self.assertContains(response, 'signup.css')


if __name__ == '__main__':
    unittest.main()
