"""
Views for payments and subscription functionality.
"""

from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse_lazy
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from apps.accounts.models import UserProfile
from common.mixins import MessageMixin, DeveloperModeMixin
from common.premium_utils import (
    is_premium_user, 
    force_premium_for_development, 
    force_premium_status_update,
    force_free_for_development,
    toggle_premium_status_for_development,
    is_development_environment
)


class SubscriptionView(LoginRequiredMixin, DeveloperModeMixin, TemplateView):
    """Display subscription information."""
    template_name = 'payments/subscription.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_profile'] = self.request.user.profile
        return context


class UpgradeView(LoginRequiredMixin, View):
    """
    Handle Premium upgrade flow with PayPal integration.
    
    This view manages the Premium upgrade process:
    - Redirects free users to PayPal payment page
    - Handles PayPal payment processing
    - Updates user subscription status after successful payment
    """
    
    def get(self, request):
        """
        Show upgrade options based on user type and environment.
        
        For free users in production: redirect to PayPal payment
        For developers in dev mode: redirect to profile configuration
        """
        user = request.user
        
        # Check if user is already Premium
        if is_premium_user(user):
            messages.info(request, 'Vous avez déjà un accès Premium !')
            return redirect('payments:subscription')
        
        # Check if developer mode is enabled
        is_dev_mode = getattr(settings, 'IS_PREMIUM_DEV_MODE', False)
        
        # Always show PayPal payment page for testing
        # In production, you can uncomment the developer mode check below
        # if is_dev_mode and is_development_environment():
        #     # Developer mode: skip payment and go directly to profile
        #     messages.info(request, 'Mode développeur actif - redirection vers la configuration du profil')
        #     return redirect('accounts:profile')
        # else:
        
        # Show PayPal payment page
        return render(request, 'payments/upgrade_payment.html')
    
    def post(self, request):
        """
        Handle PayPal payment processing and redirection.
        
        In production, this would integrate with PayPal API for secure payment processing.
        Currently simulates PayPal payment for development purposes.
        """
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'paypal':
            # Rediriger vers PayPal
            return redirect('payments:paypal_redirect')
        elif payment_method == 'stripe':
            # Rediriger vers Stripe Checkout
            return redirect('payments:stripe_checkout')
        else:
            messages.error(request, 'Méthode de paiement invalide sélectionnée.')
            return redirect('payments:upgrade')


class UpgradeSuccessView(LoginRequiredMixin, TemplateView):
    """Display success message after Premium upgrade."""
    
    template_name = 'payments/upgrade_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_premium'] = is_premium_user(self.request.user)
        return context


class PayPalRedirectView(LoginRequiredMixin, View):
    """
    Handle PayPal payment redirection.
    
    This view redirects users to PayPal for payment processing.
    In development, uses PayPal sandbox. In production, uses live PayPal.
    """
    
    def get(self, request):
        """
        Redirect user to PayPal payment page.
        
        In production, this would create a PayPal payment and redirect to PayPal.
        For development, redirects to PayPal sandbox for testing.
        """
        user = request.user
        
        # Check if user is already Premium
        if is_premium_user(user):
            messages.info(request, 'Vous avez déjà un accès Premium !')
            return redirect('payments:subscription')
        
        # Determine PayPal environment based on settings
        is_dev = is_development_environment()
        
        if is_dev:
            # Development: redirect to PayPal sandbox general page
            paypal_url = "https://www.sandbox.paypal.com/"
            messages.info(request, 'Redirection vers PayPal Sandbox pour les tests...')
        else:
            # Production: redirect to live PayPal general page
            paypal_url = "https://www.paypal.com/"
            messages.info(request, 'Redirection vers PayPal...')
        
        # Redirect to PayPal
        return redirect(paypal_url)
    
    def post(self, request):
        """
        Handle PayPal payment return.
        
        This would handle the return from PayPal after payment completion.
        """
        # In production, this would verify PayPal payment and update user status
        # For now, redirect to success page
        return redirect('payments:upgrade_success')


class PaymentWebhookView(View):
    """Handle payment webhooks from payment providers."""
    
    def post(self, request):
        """Process payment webhook."""
        # In production, this would verify webhook signatures
        # and update user subscription status accordingly
        
        # For now, return success response
        return JsonResponse({'status': 'success'})


class DowngradeView(LoginRequiredMixin, View):
    """Handle Premium downgrade to free account."""
    
    def get(self, request):
        """Show downgrade confirmation page."""
        user = request.user
        
        # Check if user is Premium
        if not is_premium_user(user):
            messages.info(request, 'Vous n\'avez pas d\'abonnement Premium actif.')
            return redirect('payments:subscription')
        
        return render(request, 'payments/downgrade_confirm.html')
    
    def post(self, request):
        """Process downgrade request."""
        user = request.user
        
        # Confirm downgrade
        if request.POST.get('confirm_downgrade') == 'yes':
            try:
                # Reset user to free account
                user.profile.subscription_type = 'free'
                user.profile.payment_completed = False
                user.profile.save()
                
                # Force update Premium status to ensure UI reflects changes immediately
                force_premium_status_update(user)
                
                messages.success(request, 'Votre abonnement Premium a été annulé avec succès. Vous avez maintenant accès aux fonctionnalités gratuites.')
                
                # Redirect to home with downgrade parameter to force UI refresh
                from django.urls import reverse
                return redirect(reverse('accounts:home') + '?downgraded=' + str(user.id))
                
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'annulation : {str(e)}')
                return redirect('payments:subscription')
        
        # User cancelled downgrade
        return redirect('payments:subscription')


# Developer Tools Views (only available in development environment)

class TogglePremiumDevView(LoginRequiredMixin, MessageMixin, View):
    """Toggle Premium status for development testing."""
    
    def post(self, request):
        """Toggle Premium status."""
        try:
            new_status = toggle_premium_status_for_development(request.user)
        except RuntimeError as e:
            pass
        except Exception as e:
            pass
        
        return redirect('payments:subscription')


class ForcePremiumDevView(LoginRequiredMixin, MessageMixin, View):
    """Force Premium status for development testing."""
    
    def post(self, request):
        """Force Premium status."""
        try:
            force_premium_for_development(request.user)
        except RuntimeError as e:
            pass
        except Exception as e:
            pass
        
        return redirect('payments:subscription')


class ForceFreeDevView(LoginRequiredMixin, MessageMixin, View):
    """Force Free status for development testing."""
    
    def post(self, request):
        """Force Free status."""
        try:
            force_free_for_development(request.user)
        except RuntimeError as e:
            pass
        except Exception as e:
            pass
        
        return redirect('payments:subscription')

# =============================================================================
# STRIPE PAYMENT VIEWS
# =============================================================================

class StripeCheckoutView(LoginRequiredMixin, View):
    """
    Gère le processus de paiement Stripe pour l'accès Premium.
    
    Cette vue crée une session de paiement Stripe et redirige l'utilisateur
    vers la page de paiement sécurisée de Stripe.
    """
    
    def get(self, request):
        """Affiche la page de paiement Stripe."""
        user = request.user
        
        # Vérifier si l'utilisateur est déjà Premium
        if is_premium_user(user):
            return redirect('payments:subscription')
        
        # Vérifier si Stripe est configuré
        from config.stripe_config import is_stripe_configured
        if not is_stripe_configured():
            messages.error(request, 'Configuration Stripe manquante. Contactez l\'administrateur.')
            return redirect('payments:upgrade')
        
        # Vérifier que l'utilisateur a un email valide
        if not user.email or not user.email.strip():
            return redirect('accounts:profile')
        
        try:
            # Créer la session de checkout Stripe
            from config.stripe_config import create_premium_checkout_session
            from django.urls import reverse
            
            success_url = request.build_absolute_uri(reverse('payments:stripe_success'))
            cancel_url = request.build_absolute_uri(reverse('payments:upgrade'))
            
            checkout_session = create_premium_checkout_session(user, success_url, cancel_url)
            
            if checkout_session:
                # Rediriger vers la page de paiement Stripe
                return redirect(checkout_session.url, code=303)
            else:
                return redirect('payments:upgrade')
                
        except Exception as e:
            return redirect('payments:upgrade')


class StripeSuccessView(LoginRequiredMixin, View):
    """
    Gère le succès du paiement Stripe et active l'accès Premium.
    
    Cette vue est appelée après un paiement Stripe réussi et met à jour
    le statut de l'utilisateur pour lui donner accès aux fonctionnalités Premium.
    """
    
    def get(self, request):
        """Traite le succès du paiement et active l'accès Premium."""
        user = request.user
        
        try:
            # Mettre à jour le profil utilisateur pour Premium
            user.profile.payment_completed = True
            user.profile.subscription_type = 'premium'
            user.profile.save()
            
            # FORÇAGE DIRECT: Utiliser la fonction spécialisée pour l'activation Premium
            from common.premium_utils import force_premium_activation, ensure_premium_ui_status
            activation_success = force_premium_activation(user)
            
            if activation_success:
                print(f"   ✅ Activation Premium forcée avec succès pour {user.username}")
            else:
                print(f"   ⚠️  Activation Premium forcée échouée pour {user.username}")
            
            # S'assurer que Premium apparaît dans l'interface utilisateur
            ui_status = ensure_premium_ui_status(user)
            print(f"   🔍 Statut Premium dans l'UI: {ui_status}")
            
            # Vérifier que Premium est bien activé
            from common.premium_utils import is_premium_user
            premium_status = is_premium_user(user)
            print(f"   🔍 Statut Premium vérifié: {premium_status}")
            
            if premium_status and ui_status:
                print(f"   🎉 Premium activé avec succès pour {user.username}")
            else:
                # Si le statut n'est toujours pas activé, forcer manuellement
                print(f"   ⚠️  Premium pas encore activé, forçage manuel...")
                
                # Forcer manuellement le statut Premium
                try:
                    # Mettre à jour le profil à nouveau
                    user.profile.refresh_from_db()
                    user.profile.subscription_type = 'premium'
                    user.profile.payment_completed = True
                    user.profile.save()
                    
                    # Forcer le cache
                    user._premium_status_cache = True
                    
                    # Vérifier à nouveau le statut UI
                    final_ui_status = ensure_premium_ui_status(user)
                    print(f"   🔄 Statut UI final après forçage: {final_ui_status}")
                    
                    if final_ui_status:
                        print(f"   ✅ Forçage manuel réussi pour {user.username}")
                    else:
                        print(f"   ⚠️  Forçage manuel partiellement réussi pour {user.username}")
                        
                except Exception as force_error:
                    print(f"   ❌ Erreur lors du forçage manuel: {force_error}")
            
            # Rediriger vers le profil après activation Premium
            return redirect('accounts:profile')
            
        except Exception as e:
            return redirect('payments:subscription')


class StripeWebhookView(View):
    """
    Gère les webhooks Stripe pour la validation des paiements.
    
    Cette vue traite les événements Stripe en arrière-plan pour
    valider les paiements et maintenir la synchronisation.
    """
    
    def post(self, request):
        """Traite les webhooks Stripe."""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        from config.stripe_config import get_stripe_webhook_secret, validate_stripe_webhook
        webhook_secret = get_stripe_webhook_secret()
        
        if not webhook_secret:
            return JsonResponse({'error': 'Configuration webhook Stripe manquante'}, status=400)
        
        # Valider la signature du webhook
        event = validate_stripe_webhook(payload, sig_header, webhook_secret)
        
        if not event:
            return JsonResponse({'error': 'Webhook invalide'}, status=400)
        
        # Traiter l'événement selon son type
        if event['type'] == 'checkout.session.completed':
            self._handle_checkout_completed(event['data']['object'])
        elif event['type'] == 'payment_intent.succeeded':
            self._handle_payment_succeeded(event['data']['object'])
        
        return JsonResponse({'status': 'success'})
    
    def _handle_checkout_completed(self, session):
        """Traite la completion d'une session de checkout."""
        user_id = session.metadata.get('user_id')
        if user_id:
            try:
                user_profile = UserProfile.objects.get(user_id=user_id)
                user_profile.payment_completed = True
                user_profile.subscription_type = 'premium'
                user_profile.save()
            except UserProfile.DoesNotExist:
                pass
    
    def _handle_payment_succeeded(self, payment_intent):
        """Traite un paiement réussi."""
        # Logique pour traiter un paiement réussi
        pass
