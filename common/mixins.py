"""
Common mixins for reusable functionality across the BeautyScan project.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from common.premium_utils import is_premium_user
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import login as django_login
from django.contrib.auth.backends import ModelBackend




class UserOwnershipMixin:
    """Mixin to ensure users can only access their own data."""
    
    def get_queryset(self):
        """Filter queryset to only show user's own data."""
        return super().get_queryset().filter(user=self.request.user)


class MessageMixin:
    """Mixin to add success/error messages to views."""
    
    def add_success_message(self, message: str) -> None:
        """Add a success message."""
        messages.success(self.request, message)
    
    def add_error_message(self, message: str) -> None:
        """Add an error message."""
        messages.error(self.request, message)
    
    def add_warning_message(self, message: str) -> None:
        """Add a warning message."""
        messages.warning(self.request, message)
    
    def add_info_message(self, message: str) -> None:
        """Add an info message."""
        messages.info(self.request, message)


class PremiumRequiredMixin:
    """
    Mixin to require Premium access for features.
    
    This mixin checks if the user has Premium access before allowing access to views.
    If the user doesn't have Premium access, it redirects them to the subscription page
    with an appropriate message.
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Check Premium status before allowing access.
        
        Args:
            request: Django request object
            *args: Additional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            HttpResponse: Redirect to subscription page if not Premium, otherwise normal dispatch
        """
        if not is_premium_user(request.user):
            messages.warning(request, 'Cette fonctionnalité nécessite un accès Premium. Veuillez passer à Premium pour continuer.')
            return redirect('payments:subscription')
        return super().dispatch(request, *args, **kwargs)


class PremiumContextMixin:
    """Mixin to add Premium status to context."""
    
    def get_context_data(self, **kwargs):
        """Add Premium status to context."""
        context = super().get_context_data(**kwargs)
        context['is_premium'] = is_premium_user(self.request.user)
        return context


class DeveloperModeMixin:
    """
    Mixin to add developer mode information to context.
    
    This mixin provides developer mode information to templates, but only for
    authorized developers. It ensures that developer tools and warnings are
    only visible to users who are explicitly authorized to see them.
    """
    
    def get_context_data(self, **kwargs):
        """
        Add developer mode information to context.
        
        Only authorized developers can see developer mode information.
        This prevents unauthorized users from seeing development tools and warnings.
        
        Returns:
            dict: Context data with developer mode information (if authorized)
        """
        context = super().get_context_data(**kwargs)
        from django.conf import settings
        from common.premium_utils import is_development_environment, is_authorized_developer
        
        # Only show developer mode information to authorized developers
        if self.request.user.is_authenticated and is_authorized_developer(self.request.user):
            context.update({
                'is_dev_mode': getattr(settings, 'IS_PREMIUM_DEV_MODE', False),
                'is_debug': getattr(settings, 'DEBUG', False),
                'is_development_environment': is_development_environment(),
                'show_dev_warnings': True,
            })
        else:
            # Hide developer mode information for unauthorized users
            context.update({
                'is_dev_mode': False,
                'is_debug': False,
                'is_development_environment': False,
                'show_dev_warnings': False,
            })
        
        return context


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware d'authentification via JWT.
    
    - Si l'utilisateur n'est pas authentifié par session, tente de valider un JWT
      présent dans l'en-tête Authorization (Bearer) ou le cookie 'access_token'.
    - En cas de token valide, connecte l'utilisateur à la session Django.
    - N'altère pas le comportement si l'utilisateur est déjà authentifié.
    """
    def process_request(self, request):
        # Déjà authentifié via session
        if getattr(request, 'user', None) and request.user.is_authenticated:
            return None
        
        if jwt_service is None:
            return None
        
        token = None
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
        elif 'access_token' in request.COOKIES:
            token = request.COOKIES.get('access_token')
        
        if not token:
            return None
        
        user = jwt_service.get_user_from_token(token)
        if user is None:
            return None
        
        # Connecter l'utilisateur à la session sans mot de passe
        backend = ModelBackend()
        user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
        try:
            django_login(request, user)
        except Exception:
            pass
        return None


class AJAXViewMixin:
    """Mixin for AJAX views with authentication and Premium access checks."""
    
    def dispatch(self, request, *args, **kwargs):
        """Check authentication and Premium access before processing request."""
        from common.premium_utils import AuthenticationHelper
        from django.http import JsonResponse
        
        # Check authentication
        is_authenticated, auth_response = AuthenticationHelper.require_authentication(request)
        if not is_authenticated:
            return JsonResponse(auth_response, status=auth_response.get('status', 401))
        
        # Check Premium access if required
        if getattr(self, 'require_premium', False):
            has_premium, premium_response = AuthenticationHelper.require_premium_access(request)
            if not has_premium:
                return JsonResponse(premium_response, status=premium_response.get('status', 403))
        
        return super().dispatch(request, *args, **kwargs)
    
    def build_success_response(self, data: dict = None, message: str = None) -> dict:
        """Build a success response."""
        from common.premium_utils import ResponseBuilder
        return ResponseBuilder.success_response(data, message)
    
    def build_error_response(self, error: str, status: int = 400, **kwargs) -> dict:
        """Build an error response."""
        from common.premium_utils import ResponseBuilder
        return ResponseBuilder.error_response(error, status, **kwargs)


class ContextEnhancerMixin:
    """Mixin to enhance context with common data."""
    
    def get_context_data(self, **kwargs):
        """Add common context data."""
        context = super().get_context_data(**kwargs)
        
        # Add user-specific data if authenticated
        if self.request.user.is_authenticated:
            context.update(self._get_user_context())
        
        # Add common data
        context.update(self._get_common_context())
        
        return context
    
    def _get_user_context(self) -> dict:
        """Get user-specific context data."""
        return {
            'user_profile': getattr(self.request.user, 'profile', None),
            'user_allergies': self._get_user_allergies(),
        }
    
    def _get_user_allergies(self) -> list:
        """Get user allergies."""
        try:
            from apps.accounts.models import Allergy
            return list(Allergy.objects.filter(user=self.request.user).values_list('name', flat=True))
        except Exception:
            return []
    
    def _get_common_context(self) -> dict:
        """Get common context data."""
        return {
            'current_page': self._get_current_page(),
        }
    
    def _get_current_page(self) -> str:
        """Get current page identifier."""
        return self.request.resolver_match.url_name if self.request.resolver_match else ''


class DemoModeMixin:
    """
    Mixin to handle demo mode display logic.
    
    Cette classe gère l'affichage du Mode Démonstration uniquement pour les utilisateurs
    non connectés afin de simplifier l'accès au scan pour les clients authentifiés.
    """
    
    def get_demo_mode_context(self) -> dict:
        """
        Get demo mode specific context data.
        
        Returns:
            dict: Context data for demo mode display
        """
        is_authenticated = self.request.user.is_authenticated
        
        return {
            'show_demo_mode': not is_authenticated,
            'is_demo_user': not is_authenticated,
            'demo_title': 'Scanner' if not is_authenticated else 'Analyser un produit',
            'demo_subtitle': 'Scannez le code-barres d\'un produit cosmétique pour l\'analyser' if not is_authenticated else 'Scannez le code-barres d\'un produit cosmétique pour obtenir une analyse détaillée',
            'show_demo_alert': not is_authenticated,
            'show_account_benefits': not is_authenticated,
        }
