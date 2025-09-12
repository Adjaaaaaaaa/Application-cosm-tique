"""
Context processors for BeautyScan.

This module provides context processors that add data to all template contexts.
"""

from django.conf import settings
from common.premium_utils import is_premium_user, is_development_environment, is_authorized_developer, get_development_environment_info


def premium_status(request):
    """
    Add Premium status to all template contexts.
    
    This allows templates to easily check if the current user has Premium access
    without needing to import the utility functions in every template.
    
    The context processor also handles developer mode visibility, ensuring that
    developer tools and warnings are only visible to authorized developers.
    """
    context = {
        'is_premium_user': False,
        'user_subscription_type': 'free',
        'is_dev_mode': False,
        'is_development_environment': False,
        'is_authorized_developer': False,
        'show_dev_warnings': False,
        'show_premium_status': False  # Control visibility of Premium status display
    }
    
    if request.user.is_authenticated:
        context['is_premium_user'] = is_premium_user(request.user)
        context['user_subscription_type'] = request.user.profile.subscription_type if hasattr(request.user, 'profile') else 'free'
        context['is_authorized_developer'] = is_authorized_developer(request.user)
        
        # Only show Premium status to authorized developers or in production
        # This prevents unauthorized users from seeing development mode information
        context['show_premium_status'] = (
            context['is_authorized_developer'] or 
            not getattr(settings, 'IS_PREMIUM_DEV_MODE', False)
        )
    
    # Add development environment information (only for authorized developers)
    if request.user.is_authenticated and context['is_authorized_developer']:
        context['is_dev_mode'] = getattr(settings, 'IS_PREMIUM_DEV_MODE', False)
        context['is_development_environment'] = is_development_environment()
        
        # Only show dev warnings to authorized developers in development environment
        context['show_dev_warnings'] = (
            context['is_dev_mode'] and 
            context['is_development_environment'] and 
            getattr(settings, 'DEBUG', False)
        )
    
    return context
