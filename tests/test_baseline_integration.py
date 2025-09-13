"""
Baseline integration tests for BeautyScan application.

These tests establish the current behavior before refactoring to Clean Architecture.
They will be used to verify that all functionality remains identical after refactoring.
"""

import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.accounts.models import UserProfile


class BaselineIntegrationTests(TestCase):
    """Test current application behavior before refactoring."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # UserProfile is automatically created by signal, just update it
        self.profile = self.user.profile
        self.profile.skin_type = 'combination'
        self.profile.age_range = '26-35'
        self.profile.save()
    
    def test_home_page_accessible(self):
        """Test that home page is accessible."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BeautyScan')
    
    def test_login_flow(self):
        """Test user login functionality."""
        # Test login page
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        
        # Test successful login
        response = self.client.post('/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_user_profile_access(self):
        """Test user profile access and data."""
        self.client.login(username='testuser', password='testpass123')
        
        # Test profile page access
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_scan_demo_page(self):
        """Test scan demo page accessibility."""
        response = self.client.get('/beautyscan/demo/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'scan')
    
    def test_user_service_profile_retrieval(self):
        """Test UserService profile retrieval functionality."""
        from backend.services.user_service import UserService
        
        service = UserService()
        profile = service.get_user_profile(self.user.id)
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile['username'], 'testuser')
        self.assertEqual(profile['skin_type'], 'combination')
        self.assertEqual(profile['age_range'], '26-35')
    
    def test_user_service_allergies_retrieval(self):
        """Test UserService allergies retrieval."""
        from backend.services.user_service import UserService
        
        # Add some allergies to the profile
        self.profile.set_allergies_list(['paraben', 'sulfate'])
        self.profile.allergies_other = 'fragrance'
        self.profile.save()
        
        service = UserService()
        allergies = service.get_user_allergies(self.user.id)
        
        self.assertIn('paraben', allergies)
        self.assertIn('sulfate', allergies)
        self.assertIn('fragrance', allergies)
    
    def test_profile_formatting_for_ai(self):
        """Test profile formatting for AI prompts."""
        from backend.services.user_service import UserService
        
        # Set up profile with various data
        self.profile.set_skin_concerns_list(['acne', 'aging'])
        self.profile.set_allergies_list(['paraben'])
        self.profile.allergies_other = 'fragrance'
        self.profile.set_dermatological_conditions_list(['eczema'])
        self.profile.set_objectives_list(['anti-aging'])
        self.profile.save()
        
        service = UserService()
        profile_data = service.get_user_profile(self.user.id)
        formatted = service.format_profile_for_ai(profile_data)
        
        # Check that formatting includes all key information
        self.assertIn('testuser', formatted)
        self.assertIn('Mixte', formatted)  # Display name for combination skin type
        self.assertIn('26–35 ans', formatted)  # Display name for age range
        self.assertIn('🚨', formatted)  # Allergy warning emoji
        self.assertIn('⚠️', formatted)  # Condition warning emoji
        self.assertIn('paraben', formatted)
        self.assertIn('fragrance', formatted)
        self.assertIn('eczema', formatted)
        self.assertIn('anti-aging', formatted)
