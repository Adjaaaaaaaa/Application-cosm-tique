"""
URL patterns for the payments app.
"""

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
    path('upgrade/', views.UpgradeView.as_view(), name='upgrade'),
    path('paypal-redirect/', views.PayPalRedirectView.as_view(), name='paypal_redirect'),
    path('downgrade/', views.DowngradeView.as_view(), name='downgrade'),
    path('upgrade-success/', views.UpgradeSuccessView.as_view(), name='upgrade_success'),
    path('webhook/', views.PaymentWebhookView.as_view(), name='payment_webhook'),
    
    # Stripe Payment URLs
    path('stripe-checkout/', views.StripeCheckoutView.as_view(), name='stripe_checkout'),
    path('stripe-success/', views.StripeSuccessView.as_view(), name='stripe_success'),
    path('stripe-webhook/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    
    # Developer Tools URLs (only available in development environment)
    path('dev/toggle-premium/', views.TogglePremiumDevView.as_view(), name='toggle_premium_dev'),
    path('dev/force-premium/', views.ForcePremiumDevView.as_view(), name='force_premium_dev'),
    path('dev/force-free/', views.ForceFreeDevView.as_view(), name='force_free_dev'),
]
