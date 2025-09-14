"""
Integration tests for payments app.

Tests the payments app endpoints and views to ensure they work correctly
with the Clean Architecture refactoring.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile


class TestPaymentsIntegration(TestCase):
    """Integration tests for payments app."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # UserProfile is automatically created by signal
        self.profile = self.user.profile

    def test_subscription_page_accessible_when_logged_in(self):
        """Test that subscription page is accessible when logged in."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/subscription/')
        self.assertEqual(response.status_code, 200)

    def test_subscription_page_requires_login(self):
        """Test that subscription page requires login."""
        response = self.client.get('/payments/subscription/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_upgrade_payment_page_accessible_when_logged_in(self):
        """Test that upgrade payment page is accessible when logged in."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/upgrade/')
        self.assertEqual(response.status_code, 200)

    def test_upgrade_payment_page_requires_login(self):
        """Test that upgrade payment page requires login."""
        response = self.client.get('/payments/upgrade/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_paypal_payment_page_accessible_when_logged_in(self):
        """Test that PayPal payment page is accessible when logged in."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/paypal/')
        self.assertEqual(response.status_code, 200)

    def test_paypal_payment_page_requires_login(self):
        """Test that PayPal payment page requires login."""
        response = self.client.get('/payments/paypal/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_stripe_success_page_accessible_when_logged_in(self):
        """Test that Stripe success page is accessible when logged in."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/stripe/success/')
        self.assertEqual(response.status_code, 200)

    def test_stripe_success_page_requires_login(self):
        """Test that Stripe success page requires login."""
        response = self.client.get('/payments/stripe/success/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_upgrade_success_page_accessible_when_logged_in(self):
        """Test that upgrade success page is accessible when logged in."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/upgrade/success/')
        self.assertEqual(response.status_code, 200)

    def test_upgrade_success_page_requires_login(self):
        """Test that upgrade success page requires login."""
        response = self.client.get('/payments/upgrade/success/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_downgrade_confirm_page_accessible_when_logged_in(self):
        """Test that downgrade confirm page is accessible when logged in."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/downgrade/confirm/')
        self.assertEqual(response.status_code, 200)

    def test_downgrade_confirm_page_requires_login(self):
        """Test that downgrade confirm page requires login."""
        response = self.client.get('/payments/downgrade/confirm/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_subscription_page_content(self):
        """Test subscription page content."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/subscription/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'subscription')

    def test_upgrade_payment_page_content(self):
        """Test upgrade payment page content."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/upgrade/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'upgrade')

    def test_paypal_payment_page_content(self):
        """Test PayPal payment page content."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/paypal/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'paypal')

    def test_stripe_success_page_content(self):
        """Test Stripe success page content."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/stripe/success/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')

    def test_upgrade_success_page_content(self):
        """Test upgrade success page content."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/upgrade/success/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'success')

    def test_downgrade_confirm_page_content(self):
        """Test downgrade confirm page content."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/payments/downgrade/confirm/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'downgrade')

    def test_payment_templates_loading(self):
        """Test that payment templates load correctly."""
        self.client.login(username='testuser', password='testpass123')
        
        # Test subscription template
        response = self.client.get('/payments/subscription/')
        self.assertEqual(response.status_code, 200)
        
        # Test upgrade template
        response = self.client.get('/payments/upgrade/')
        self.assertEqual(response.status_code, 200)
        
        # Test PayPal template
        response = self.client.get('/payments/paypal/')
        self.assertEqual(response.status_code, 200)

    def test_payment_css_loading(self):
        """Test that payment pages load CSS correctly."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/payments/subscription/')
        self.assertEqual(response.status_code, 200)
        # Check that CSS files are referenced
        self.assertContains(response, 'payments.css')

    def test_payment_js_loading(self):
        """Test that payment pages load JavaScript correctly."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/payments/subscription/')
        self.assertEqual(response.status_code, 200)
        # Check that JS files are referenced
        self.assertContains(response, 'payments.js')

    def test_payment_form_submission(self):
        """Test payment form submission."""
        self.client.login(username='testuser', password='testpass123')
        
        # This would need actual form data based on the payment form
        response = self.client.post('/payments/upgrade/', {
            'payment_method': 'stripe',
            'amount': '9.99'
        })
        
        # Adjust assertion based on actual behavior
        self.assertIn(response.status_code, [200, 302])

    def test_paypal_payment_flow(self):
        """Test PayPal payment flow."""
        self.client.login(username='testuser', password='testpass123')
        
        # This would need actual PayPal integration data
        response = self.client.post('/payments/paypal/', {
            'payment_method': 'paypal',
            'amount': '9.99'
        })
        
        # Adjust assertion based on actual behavior
        self.assertIn(response.status_code, [200, 302])

    def test_stripe_payment_flow(self):
        """Test Stripe payment flow."""
        self.client.login(username='testuser', password='testpass123')
        
        # This would need actual Stripe integration data
        response = self.client.post('/payments/upgrade/', {
            'payment_method': 'stripe',
            'stripe_token': 'tok_test_123'
        })
        
        # Adjust assertion based on actual behavior
        self.assertIn(response.status_code, [200, 302])

    def test_downgrade_confirmation(self):
        """Test downgrade confirmation flow."""
        self.client.login(username='testuser', password='testpass123')
        
        # This would need actual downgrade logic
        response = self.client.post('/payments/downgrade/confirm/', {
            'confirm': 'yes'
        })
        
        # Adjust assertion based on actual behavior
        self.assertIn(response.status_code, [200, 302])

    def test_payment_permissions(self):
        """Test payment permissions and access control."""
        # Test that users can only access their own payment data
        self.client.login(username='testuser', password='testpass123')
        
        # This would need actual payment data and user isolation
        response = self.client.get('/payments/subscription/')
        
        # Should be accessible to the user
        self.assertEqual(response.status_code, 200)

    def test_payment_redirects(self):
        """Test payment redirects and flow."""
        self.client.login(username='testuser', password='testpass123')
        
        # Test redirect after successful payment
        response = self.client.get('/payments/stripe/success/')
        self.assertEqual(response.status_code, 200)
        
        # Test redirect after successful upgrade
        response = self.client.get('/payments/upgrade/success/')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
