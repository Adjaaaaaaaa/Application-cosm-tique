"""
Profile view adapter for Clean Architecture.

This adapter transforms the Django profile view to use Clean Architecture
use cases while maintaining the same interface and behavior.
"""

import logging
from typing import Dict, Any, Optional
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse

from usecases.user.get_user_profile import GetUserProfileUseCase
from usecases.user.update_user_profile import UpdateUserProfileUseCase
from infrastructure.repositories.django_user_repository import DjangoUserRepository
from infrastructure.repositories.django_profile_repository import DjangoProfileRepository
from core.exceptions import UserNotFoundError, ProfileNotFoundError

logger = logging.getLogger(__name__)


class ProfileViewAdapter:
    """
    Adapter for profile view using Clean Architecture.
    
    This adapter handles the profile view logic using use cases
    while maintaining the same interface as the original view.
    """
    
    def __init__(self):
        """Initialize adapter with repositories and use cases."""
        # Create repositories
        self._user_repository = DjangoUserRepository()
        self._profile_repository = DjangoProfileRepository()
        
        # Create use cases
        self._get_user_profile_use_case = GetUserProfileUseCase(
            self._user_repository,
            self._profile_repository
        )
        self._update_user_profile_use_case = UpdateUserProfileUseCase(
            self._user_repository,
            self._profile_repository
        )
    
    def handle_profile_view(self, request: HttpRequest) -> HttpResponse:
        """
        Handle profile view request using Clean Architecture.
        
        Args:
            request: Django HTTP request
            
        Returns:
            Django HTTP response
        """
        try:
            # Get user profile using use case
            profile_data = self._get_user_profile_use_case.execute(request.user.id)
            
            if request.method == 'POST':
                return self._handle_profile_update(request, profile_data)
            else:
                return self._render_profile_form(request, profile_data)
                
        except (UserNotFoundError, ProfileNotFoundError) as e:
            logger.error(f"Profile view error: {str(e)}")
            messages.error(request, "Erreur lors du chargement du profil.")
            return redirect('home')
        except Exception as e:
            logger.error(f"Unexpected error in profile view: {str(e)}")
            messages.error(request, "Une erreur inattendue s'est produite.")
            return redirect('home')
    
    def _handle_profile_update(self, request: HttpRequest, profile_data: Dict[str, Any]) -> HttpResponse:
        """
        Handle profile update using Clean Architecture.
        
        Args:
            request: Django HTTP request
            profile_data: Current profile data
            
        Returns:
            Django HTTP response
        """
        try:
            # Extract form data
            form_data = self._extract_form_data(request)
            
            # Update profile using use case
            updated_profile = self._update_user_profile_use_case.execute(
                request.user.id,
                form_data
            )
            
            if updated_profile:
                messages.success(request, "Profil mis à jour avec succès !")
                return redirect('profile')
            else:
                messages.error(request, "Erreur lors de la mise à jour du profil.")
                return self._render_profile_form(request, profile_data)
                
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            messages.error(request, "Erreur lors de la mise à jour du profil.")
            return self._render_profile_form(request, profile_data)
    
    def _extract_form_data(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Extract and validate form data from request.
        
        Args:
            request: Django HTTP request
            
        Returns:
            Dictionary of form data
        """
        return {
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'email': request.POST.get('email', ''),
            'skin_type': request.POST.get('skin_type', ''),
            'age_range': request.POST.get('age_range', ''),
            'skin_concerns': request.POST.getlist('skin_concerns'),
            'dermatological_conditions': request.POST.getlist('dermatological_conditions'),
            'dermatological_other': request.POST.get('dermatological_other', ''),
            'allergies': request.POST.getlist('allergies'),
            'allergies_other': request.POST.get('allergies_other', ''),
            'product_style': request.POST.get('product_style', ''),
            'routine_frequency': request.POST.get('routine_frequency', ''),
            'objectives': request.POST.getlist('objectives'),
            'budget': request.POST.get('budget', ''),
        }
    
    def _render_profile_form(self, request: HttpRequest, profile_data: Dict[str, Any]) -> HttpResponse:
        """
        Render profile form with data.
        
        Args:
            request: Django HTTP request
            profile_data: Profile data to display
            
        Returns:
            Django HTTP response
        """
        # Import here to avoid circular imports
        from apps.accounts.forms import UserProfileForm
        
        # Create form with profile data
        form = UserProfileForm(initial=profile_data)
        
        return render(request, 'accounts/profile.html', {
            'form': form,
            'profile': profile_data
        })


# Create global adapter instance
profile_view_adapter = ProfileViewAdapter()


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """
    Profile view using Clean Architecture adapter.
    
    This view maintains the same interface as the original
    while using Clean Architecture internally.
    """
    return profile_view_adapter.handle_profile_view(request)
