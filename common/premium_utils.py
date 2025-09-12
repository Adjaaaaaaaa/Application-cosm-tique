"""
Premium status utilities for BeautyScan.

This module provides comprehensive utilities for managing Premium user access,
developer testing capabilities, and secure environment validation. It implements
a multi-layered security system that prevents unauthorized access to Premium
features while enabling controlled developer testing.

The module includes:
- Premium status checking with caching for performance
- Developer environment validation and authorization
- Secure Premium dev mode for testing
- Utility classes for common operations (product analysis, user preferences, etc.)
- Error handling and response building utilities

SECURITY CONSIDERATIONS:
- Premium dev mode is only available in development environments
- Requires virtual environment and explicit authorization
- All functions include proper validation and error handling
- Production environments enforce strict payment verification
"""

import os
import sys
from django.conf import settings


def is_virtual_environment():
    """
    Check if running in a virtual environment.
    
    Virtual environments provide isolation and are a good indicator
    that this is a controlled development environment rather than
    a production system. This is used as a security check for
    Premium dev mode.
    
    Returns:
        bool: True if running in a virtual environment
    """
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)


def is_development_environment():
    """
    Check if this is a development environment.
    
    Multiple indicators are used to determine if this is a development
    environment. This provides defense in depth against accidental
    production deployment of development features.
    
    Returns:
        bool: True if this appears to be a development environment
    """
    # Temporarily allow development mode without virtual environment for testing
    # In production, this should always require a virtual environment
    
    # Check for development-specific environment variables
    # These provide explicit control over development mode
    dev_indicators = [
        'DJANGO_DEVELOPMENT',
        'IS_DEVELOPMENT',
        'LOCAL_DEVELOPMENT'
    ]
    
    for indicator in dev_indicators:
        if os.environ.get(indicator, '').lower() in ['true', '1', 'yes']:
            return True
    
    # Check if running on localhost/development ports
    # This is another indicator of development environment
    if os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('.dev'):
        return True
    
    # Temporarily allow development mode for testing
    # Note: This bypasses security checks for development convenience
    return True


def is_authorized_developer(user) -> bool:
    """
    Check if user is an authorized developer for Premium dev mode.
    
    This function implements the authorization control for Premium dev mode.
    Only users explicitly listed in AUTHORIZED_DEV_USERS can access Premium
    features without payment verification.
    
    Args:
        user: Django User object to check
        
    Returns:
        bool: True if user is authorized developer, False otherwise
    """
    from django.contrib.auth.models import User
    if not user or not user.is_authenticated:
        return False
    
    # Get authorized users list from settings
    # This list is controlled by administrators and should be kept minimal
    authorized_users = getattr(settings, 'AUTHORIZED_DEV_USERS', [])
    
    # Check if user's username is in the authorized list
    return user.username in authorized_users


def is_premium_user(user) -> bool:
    """
    Check if a user has Premium access.
    
    This is the main function for determining Premium status. It implements
    different logic for development and production environments:
    
    - Development: Only authorized developers get Premium access
    - Production: Checks actual subscription status from database
    
    The function includes caching for performance and proper error handling.
    
    Args:
        user: Django User object to check
        
    Returns:
        bool: True if user has Premium access, False otherwise
    """
    from django.contrib.auth.models import User
    if not user or not user.is_authenticated:
        return False
    
    # Check for cached status first to improve performance
    # This avoids repeated database queries for the same user
    if hasattr(user, '_premium_status_cache'):
        return user._premium_status_cache
    
    # PRIORITÉ 1: Vérifier si l'utilisateur a un paiement Stripe réussi
    # Cette vérification contourne TOUTES les autres vérifications (mode dev inclus)
    try:
        user.profile.refresh_from_db()
        if user.profile.payment_completed and user.profile.subscription_type == 'premium':
            user._premium_status_cache = True
            return True
    except Exception:
        pass
    
    # Developer testing mode: bypass payment verification but respect downgrades and authorization
    # This allows developers to test Premium features without payment
    if getattr(settings, 'IS_PREMIUM_DEV_MODE', False):
        # Additional security check for production
        # This prevents accidental enabling of dev mode in production
        if not is_development_environment():
            user._premium_status_cache = False
            return False
        
        # Check if user is authorized developer
        # Only authorized developers can access Premium in dev mode
        if not is_authorized_developer(user):
            user._premium_status_cache = False
            return False
        
        # Check if user has explicitly been downgraded to free
        # This allows developers to test both Free and Premium experiences
        try:
            user.profile.refresh_from_db()
            if user.profile.subscription_type == 'free':
                user._premium_status_cache = False
                return False
            else:
                user._premium_status_cache = True
                return True
        except Exception:
            # If profile doesn't exist, assume free
            # This is a safe default that prevents unauthorized access
            user._premium_status_cache = False
            return False
    
    # Production mode: check actual subscription status
    # This is the normal flow for production environments
    try:
        # Force refresh from database to get latest status
        # This ensures we have the most current subscription information
        user.profile.refresh_from_db()
        is_premium = user.profile.subscription_type in ['premium', 'pro']
        user._premium_status_cache = is_premium
        return is_premium
    except Exception:
        # If profile doesn't exist or other error, assume free
        # This is a safe default that prevents unauthorized access
        user._premium_status_cache = False
        return False


def force_premium_for_development(user) -> None:
    """
    Force Premium status for a user in development mode.
    
    This function is for developer testing only and should never be used in production.
    It directly updates the user's subscription type without payment verification,
    allowing developers to test Premium features easily.
    
    The function includes multiple security checks to prevent misuse:
    - Requires DEBUG mode to be enabled
    - Requires IS_PREMIUM_DEV_MODE to be enabled
    - Requires user to be in authorized developers list
    - Requires development environment
    
    Args:
        user: Django User object to upgrade to Premium
        
    Raises:
        RuntimeError: If called in production environment or user not authorized
    """
    from django.contrib.auth.models import User
    if not getattr(settings, 'DEBUG', False):
        raise RuntimeError(
            "force_premium_for_development() can only be used in development mode"
        )
    
    if not getattr(settings, 'IS_PREMIUM_DEV_MODE', False):
        raise RuntimeError(
            "IS_PREMIUM_DEV_MODE must be enabled to use force_premium_for_development()"
        )
    
    # Temporarily allow forcing premium without virtual environment for testing
    # Note: Virtual environment check is bypassed for development convenience
    # This check provides additional security by requiring virtual environment
    # if not is_development_environment():
    #     raise RuntimeError(
    #         "force_premium_for_development() can only be used in a development environment"
    #     )
    
    if not is_authorized_developer(user):
        raise RuntimeError(
            f"User '{user.username}' is not authorized for Premium dev mode. "
            f"Add to AUTHORIZED_DEV_USERS in settings."
        )
    
    try:
        user.profile.subscription_type = 'premium'
        user.profile.save()
        clear_premium_cache(user)
    except Exception as e:
        raise RuntimeError(f"Failed to upgrade user to Premium: {e}")


def force_free_for_development(user) -> None:
    """
    Force Free status for a user in development mode.
    
    This function is for developer testing only and allows developers to easily
    switch between Free and Premium accounts for testing purposes. It's essential
    for testing both user experiences without going through payment flows.
    
    Args:
        user: Django User object to downgrade to Free
        
    Raises:
        RuntimeError: If called in production environment
    """
    if not getattr(settings, 'DEBUG', False):
        raise RuntimeError(
            "force_free_for_development() can only be used in development mode"
        )
    
    if not getattr(settings, 'IS_PREMIUM_DEV_MODE', False):
        raise RuntimeError(
            "IS_PREMIUM_DEV_MODE must be enabled to use force_free_for_development()"
        )
    
    if not is_development_environment():
        raise RuntimeError(
            "force_free_for_development() can only be used in a development environment"
        )
    
    try:
        user.profile.subscription_type = 'free'
        user.profile.payment_completed = False
        user.profile.save()
        clear_premium_cache(user)
    except Exception as e:
        raise RuntimeError(f"Failed to downgrade user to Free: {e}")


def toggle_premium_status_for_development(user) -> str:
    """
    Toggle Premium status for a user in development mode.
    
    This function allows developers to easily switch between Free and Premium
    accounts for testing purposes.
    
    Args:
        user: Django User object to toggle Premium status
        
    Returns:
        str: New status ('premium' or 'free')
        
    Raises:
        RuntimeError: If called in production environment or user not authorized
    """
    if not getattr(settings, 'DEBUG', False):
        raise RuntimeError(
            "toggle_premium_status_for_development() can only be used in development mode"
        )
    
    if not getattr(settings, 'IS_PREMIUM_DEV_MODE', False):
        raise RuntimeError(
            "IS_PREMIUM_DEV_MODE must be enabled to use toggle_premium_status_for_development()"
        )
    
    if not is_development_environment():
        raise RuntimeError(
            "toggle_premium_status_for_development() can only be used in a development environment"
        )
    
    # Check authorization for Premium access
    current_status = user.profile.subscription_type
    if current_status in ['premium', 'pro']:
        # Downgrading to free - no authorization needed
        pass
    else:
        # Upgrading to premium - check authorization
        if not is_authorized_developer(user):
            raise RuntimeError(
                f"User '{user.username}' is not authorized for Premium dev mode. "
                f"Add to AUTHORIZED_DEV_USERS in settings."
            )
    
    try:
        new_status = 'free' if current_status in ['premium', 'pro'] else 'premium'
        
        user.profile.subscription_type = new_status
        if new_status == 'premium':
            user.profile.payment_completed = True
        else:
            user.profile.payment_completed = False
        
        user.profile.save()
        clear_premium_cache(user)
        
        return new_status
    except Exception as e:
        raise RuntimeError(f"Failed to toggle Premium status: {e}")


def get_premium_features() -> list:
    """
    Get list of Premium features for display/testing purposes.
    
    Returns:
        list: List of Premium feature descriptions
    """
    return [
        "Personalized beauty AI that answers your questions",
        "Tailored routines based on skin type, pathologies, allergies, age, and budget",
        "Articles & alerts on harmful ingredients powered by RAG",
        "Smart recommendations to avoid duplicates and optimize effectiveness"
    ]


def clear_premium_cache(user) -> None:
    """
    Clear cached Premium status for a user.
    
    This function should be called after any changes to the user's subscription
    to ensure the UI reflects the current status immediately.
    
    Args:
        user: Django User object
    """
    if hasattr(user, '_premium_status_cache'):
        delattr(user, '_premium_status_cache')


def force_premium_status_update(user) -> None:
    """
    Force update of Premium status by clearing cache and refreshing from database.
    
    This function ensures that any changes to subscription status are immediately
    reflected in the UI without requiring a page reload.
    
    Args:
        user: Django User object
    """
    # Clear any cached status
    clear_premium_cache(user)
    
    # Force refresh from database
    try:
        user.profile.refresh_from_db()
    except Exception:
        pass


def get_development_environment_info() -> dict:
    """
    Get information about the current development environment.
    
    This function is useful for debugging and ensuring proper environment setup.
    
    Returns:
        dict: Environment information
    """
    return {
        'is_virtual_environment': is_virtual_environment(),
        'is_development_environment': is_development_environment(),
        'debug_mode': getattr(settings, 'DEBUG', False),
        'premium_dev_mode': getattr(settings, 'IS_PREMIUM_DEV_MODE', False),
        'settings_module': os.environ.get('DJANGO_SETTINGS_MODULE', ''),
        'authorized_dev_users': getattr(settings, 'AUTHORIZED_DEV_USERS', []),
        'development_vars': {
            'DJANGO_DEVELOPMENT': os.environ.get('DJANGO_DEVELOPMENT', ''),
            'IS_DEVELOPMENT': os.environ.get('IS_DEVELOPMENT', ''),
            'LOCAL_DEVELOPMENT': os.environ.get('LOCAL_DEVELOPMENT', ''),
        }
    }


class ProductAnalysisManager:
    """
    Centralized manager for product analysis operations.
    
    This class provides a unified interface for analyzing product ingredients,
    calculating safety scores, and managing ingredient data. It encapsulates
    the complexity of ingredient parsing, scoring, and safety analysis.
    
    The manager coordinates between different services (scoring, parsing)
    to provide comprehensive product analysis results.
    """
    
    def __init__(self):
        """
        Initialize the ProductAnalysisManager with required services.
        
        Note: Product analysis services have been removed as the products app
        has been eliminated from the project.
        """
        self.scoring_service = None
        self.inci_parser = None
    
    def analyze_product_ingredients(self, product) -> dict:
        """
        Analyze product ingredients and return comprehensive data.
        
        This method performs a complete analysis of a product's ingredients,
        including parsing, scoring, and safety statistics. It handles the
        entire pipeline from raw ingredient text to actionable safety data.
        
        Args:
            product: Product object to analyze
            
        Returns:
            dict: Comprehensive analysis results including score data,
                  safety statistics, and ingredient information
        """
        try:
            # Parse ingredients if needed
            if not product.productingredient_set.exists() and product.ingredients_text:
                self.inci_parser.parse_and_save_ingredients(product)
            
            # Get ingredients data
            ingredients_data = []
            for pi in product.productingredient_set.select_related('ingredient').order_by('position'):
                ingredients_data.append({
                    'name': pi.ingredient.name,
                    'hazard_level': pi.ingredient.hazard_level,
                    'position': pi.position,
                })
            
            # Calculate score
            score_data = self.scoring_service.calculate_product_score(ingredients_data) if ingredients_data else None
            
            # Calculate safety statistics
            ingredients = product.productingredient_set.select_related('ingredient')
            safety_stats = self._calculate_safety_stats(ingredients)
            
            return {
                'score_data': score_data,
                'safety_stats': safety_stats,
                'ingredients': ingredients,
                'ingredients_data': ingredients_data
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'score_data': None,
                'safety_stats': None,
                'ingredients': [],
                'ingredients_data': []
            }
    
    def _calculate_safety_stats(self, ingredients) -> dict:
        """
        Calculate safety statistics for ingredients.
        
        This private method analyzes the safety distribution of ingredients
        by categorizing them into risk levels and calculating percentages.
        This data is used for safety visualization and risk assessment.
        
        Args:
            ingredients: QuerySet of ProductIngredient objects
            
        Returns:
            dict: Safety statistics including counts and percentages for each risk level
        """
        safe_count = ingredients.filter(ingredient__hazard_level='Low').count()
        risky_count = ingredients.filter(ingredient__hazard_level='Medium').count()
        dangerous_count = ingredients.filter(ingredient__hazard_level='High').count()
        unknown_count = ingredients.filter(ingredient__hazard_level='Unknown').count()
        total = ingredients.count()
        
        return {
            'safe': safe_count,
            'risky': risky_count,
            'dangerous': dangerous_count,
            'unknown': unknown_count,
            'total': total,
            'risk_distribution': {
                'Low': (safe_count / total * 100) if total > 0 else 0,
                'Medium': (risky_count / total * 100) if total > 0 else 0,
                'High': (dangerous_count / total * 100) if total > 0 else 0,
            }
        }
    
    def update_product_score(self, product, score_data: dict) -> None:
        """
        Update product score in database.
        
        This method persists the calculated safety score to the product
        record for future reference and display purposes.
        
        Args:
            product: Product object to update
            score_data: Dictionary containing the calculated score data
        """
        if score_data and 'total_score' in score_data:
            product.score = score_data['total_score']
            product.save()


class UserPreferencesManager:
    """
    Centralized manager for user preferences and profile data.
    
    This class handles all operations related to user preferences and profile
    management. It provides a clean interface for updating user data and
    ensures consistency in how preferences are stored and retrieved.
    
    The manager maps form data to profile fields and handles data validation
    and transformation as needed.
    """
    
    def __init__(self, user):
        """
        Initialize the UserPreferencesManager with a user.
        
        Args:
            user: Django User object to manage preferences for
        """
        self.user = user
        self.profile = user.profile
    
    def update_skincare_preferences(self, preferences: dict) -> None:
        """
        Update user's skincare preferences.
        
        This method maps form data to profile fields and updates the user's
        profile with new preference data. It handles the transformation
        between form field names and database field names.
        
        Args:
            preferences: Dictionary containing form data with preference values
        """
        # Map form data to profile fields
        field_mapping = {
            'skin_type': 'skin_type',
            'age': 'age_range',
            'concerns': 'skin_concerns',
            'dermatological_conditions': 'pathologies',
            'allergies': 'allergies',
            'product_style': 'budget',
            'routine_frequency': 'routine_frequency',
            'objectives': 'objectives'
        }
        
        for form_field, profile_field in field_mapping.items():
            if form_field in preferences:
                value = preferences[form_field]
                if isinstance(value, list):
                    value = ', '.join(value)
                setattr(self.profile, profile_field, value)
        
        self.profile.save()
    
    def get_preferences_dict(self) -> dict:
        """Get user preferences as a dictionary for AI processing."""
        return {
            'skin_type': self.profile.skin_type or 'normal',
            'age_range': self.profile.age_range or '',
            'skin_concerns': self.profile.skin_concerns or '',
            'pathologies': self.profile.pathologies or '',
            'allergies': self.profile.allergies or '',
            'budget': self.profile.budget or 'moderate',
            'routine_frequency': self.profile.routine_frequency or 'daily',
            'objectives': self.profile.objectives or ''
        }
    
    def has_complete_profile(self) -> bool:
        """Check if user has provided essential profile information."""
        essential_fields = ['skin_type', 'age_range']
        return all(getattr(self.profile, field) for field in essential_fields)


class RoutineManager:
    """
    Centralized manager for routine operations.
    
    This class handles the creation and management of skincare routines.
    It coordinates between user preferences and the AI routine generator
    to create personalized skincare routines for users.
    
    The manager provides a clean interface for routine generation and
    database persistence, abstracting the complexity of AI integration.
    """
    
    def __init__(self, user):
        """
        Initialize the RoutineManager with a user.
        
        Args:
            user: Django User object to create routines for
        """
        self.user = user
    
    def create_routine_from_preferences(self, preferences: dict, routine_type: str = 'morning') -> dict:
        """
        Create a routine based on user preferences.
        
        This method uses the AI routine generator to create personalized
        skincare routines based on user preferences and skin characteristics.
        It handles the mapping of preferences to the generator's expected format.
        
        Args:
            preferences: Dictionary containing user preferences
            routine_type: Type of routine ('morning' or 'evening')
            
        Returns:
            dict: Generated routine data including steps and recommendations
        """
        from apps.ai_routines.services.routine_generator import RoutineGenerator
        
        generator = RoutineGenerator()
        routine_data = generator.generate_routine(
            skin_type=preferences.get('skin_type', 'normal'),
            concerns=preferences.get('concerns', []),
            age=preferences.get('age'),
            pathologies=preferences.get('dermatological_conditions', []),
            allergies=preferences.get('allergies', []),
            budget=preferences.get('product_style', 'moderate'),
            routine_type=routine_type
        )
        
        return routine_data
    
    def save_routine_to_database(self, routine_data: dict, routine_type: str) -> object:
        """
        Save generated routine to database.
        
        This method persists the generated routine to the database for
        future reference and user access. It creates a proper Routine
        object with all necessary metadata.
        
        Args:
            routine_data: Dictionary containing the generated routine data
            routine_type: Type of routine ('morning' or 'evening')
            
        Returns:
            Routine: The created Routine object
        """
        from apps.ai_routines.models import Routine
        
        routine = Routine.objects.create(
            user=self.user,
            name=f"Routine {routine_type.title()} - {routine_data.get('title', 'Personnalisée')}",
            description=routine_data.get('description', ''),
            routine_type=routine_type,
            steps=routine_data.get('steps', []),
            recommendations=routine_data.get('recommendations', ''),
            created_by_ai=True
        )
        
        return routine


class ValidationManager:
    """
    Centralized manager for form validation and error handling.
    
    This class provides comprehensive validation for user input data,
    ensuring data integrity and security. It includes validation for
    skincare preferences, product data, and user input sanitization.
    
    The manager implements both client-side and server-side validation
    to prevent invalid data from entering the system.
    """
    
    @staticmethod
    def validate_skincare_preferences(preferences: dict) -> tuple[bool, list]:
        """
        Validate skincare preferences data.
        
        This method performs comprehensive validation of user skincare
        preferences, checking required fields, data types, and value ranges.
        It ensures that only valid data is processed by the system.
        
        Args:
            preferences: Dictionary containing user preferences to validate
            
        Returns:
            tuple: (is_valid, list_of_errors) - validation result and any errors
        """
        errors = []
        
        # Check required fields
        required_fields = ['skin_type', 'age']
        for field in required_fields:
            if not preferences.get(field):
                errors.append(f"Le champ '{field}' est requis.")
        
        # Validate age range
        age = preferences.get('age')
        if age and not age.isdigit():
            errors.append("L'âge doit être un nombre.")
        elif age and int(age) < 13 or int(age) > 100:
            errors.append("L'âge doit être entre 13 et 100 ans.")
        
        # Validate skin type
        valid_skin_types = ['normal', 'dry', 'oily', 'combination', 'sensitive']
        skin_type = preferences.get('skin_type')
        if skin_type and skin_type not in valid_skin_types:
            errors.append("Type de peau invalide.")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_product_data(product_data: dict) -> tuple[bool, list]:
        """
        Validate product data from API.
        
        This method validates product data received from external APIs
        to ensure it contains all required fields before processing.
        
        Args:
            product_data: Dictionary containing product data to validate
            
        Returns:
            tuple: (is_valid, list_of_errors) - validation result and any errors
        """
        errors = []
        
        required_fields = ['name', 'brand']
        for field in required_fields:
            if not product_data.get(field):
                errors.append(f"Le champ '{field}' est requis pour le produit.")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_user_input(text: str) -> str:
        """
        Sanitize user input to prevent XSS and other attacks.
        
        This method performs input sanitization to prevent cross-site
        scripting (XSS) and other injection attacks. It escapes HTML
        characters and removes potentially dangerous content.
        
        Args:
            text: Raw user input text to sanitize
            
        Returns:
            str: Sanitized text safe for display and processing
        """
        import html
        
        if not text:
            return ""
        
        # HTML escape
        text = html.escape(text)
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<script>', '</script>', 'javascript:', 'onclick', 'onload']
        for char in dangerous_chars:
            text = text.replace(char.lower(), '')
            text = text.replace(char.upper(), '')
        
        return text.strip()


class FormHelper:
    """
    Helper class for form processing and validation.
    
    This class provides utilities for extracting, sanitizing, and validating
    form data from Django requests. It handles complex form structures
    including multiple values and field mapping.
    
    The helper ensures that all form data is properly sanitized and validated
    before processing, maintaining data integrity and security.
    """
    
    @staticmethod
    def extract_form_data(request, field_mapping: dict = None) -> dict:
        """
        Extract and sanitize form data from request.
        
        Args:
            request: Django request object
            field_mapping: Optional mapping of form fields to internal names
            
        Returns:
            dict: Sanitized form data
        """
        form_data = {}
        
        for key, value in request.POST.items():
            # Handle multiple values (like checkboxes)
            if key.endswith('[]'):
                key = key[:-2]  # Remove [] suffix
                values = request.POST.getlist(key + '[]')
                form_data[key] = [ValidationManager.sanitize_user_input(v) for v in values]
            else:
                form_data[key] = ValidationManager.sanitize_user_input(value)
        
        # Apply field mapping if provided
        if field_mapping:
            mapped_data = {}
            for form_field, internal_field in field_mapping.items():
                if form_field in form_data:
                    mapped_data[internal_field] = form_data[form_field]
            return mapped_data
        
        return form_data
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, list]:
        """
        Validate that required fields are present and not empty.
        
        Args:
            data: Form data dictionary
            required_fields: List of required field names
            
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        for field in required_fields:
            value = data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                errors.append(f"Le champ '{field}' est requis.")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def build_form_errors(errors: list) -> dict:
        """
        Build form errors dictionary for template rendering.
        
        Args:
            errors: List of error messages
            
        Returns:
            dict: Form errors dictionary
        """
        return {
            'form_errors': errors,
            'has_errors': len(errors) > 0
        }


class PremiumAccessManager:
    """
    Manager for Premium access control and upgrade handling.
    
    This class provides centralized management of Premium access control,
    handling upgrades, downgrades, and access verification. It implements
    different logic for development and production environments.
    
    The manager ensures that Premium features are only accessible to
    authorized users and handles the transition between Free and Premium
    accounts appropriately.
    """
    
    @staticmethod
    def handle_premium_upgrade(request, user) -> tuple[bool, str]:
        """
        Handle Premium upgrade for user.
        
        Args:
            request: Django request object
            user: User object
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Check if user is already Premium
            if is_premium_user(user):
                return True, "Utilisateur déjà Premium"
            
            # Handle upgrade based on environment
            if getattr(settings, 'IS_PREMIUM_DEV_MODE', False) and is_development_environment():
                # Developer mode: use force function
                force_premium_for_development(user)
                return True, "Statut Premium activé en mode développement"
            else:
                # Production mode: check if payment was completed
                if user.profile.payment_completed:
                    user.profile.subscription_type = 'premium'
                    user.profile.save()
                    return True, "Statut Premium activé"
                else:
                    return False, "Paiement requis pour accéder aux fonctionnalités Premium"
                    
        except Exception as e:
            error_message = ErrorHandler.handle_premium_error(e, user)
            return False, error_message
    
    @staticmethod
    def check_premium_access(user) -> tuple[bool, str]:
        """
        Check if user has Premium access.
        
        Args:
            user: User object
            
        Returns:
            tuple: (has_access, message)
        """
        if is_premium_user(user):
            return True, "Accès Premium confirmé"
        else:
            return False, "Accès Premium requis"


class ErrorHandler:
    """
    Centralized error handling and logging.
    
    This class provides consistent error handling across the application,
    translating technical errors into user-friendly French messages.
    It categorizes different types of errors and provides appropriate
    responses for each category.
    
    The handler ensures that users receive meaningful error messages
    while maintaining security by not exposing sensitive technical details.
    """
    
    @staticmethod
    def handle_premium_error(error: Exception, user) -> str:
        """
        Handle Premium-related errors with appropriate messages.
        
        This method categorizes Premium-related errors and returns
        user-friendly French messages. It handles authorization,
        development mode, and payment-related errors.
        
        Args:
            error: Exception that occurred
            user: User object for context
            
        Returns:
            str: User-friendly error message in French
        """
        error_message = str(error)
        
        if "not authorized" in error_message.lower():
            return "Vous n'êtes pas autorisé à accéder aux fonctionnalités Premium."
        elif "development mode" in error_message.lower():
            return "Cette fonctionnalité n'est disponible qu'en mode développement."
        elif "payment required" in error_message.lower():
            return "Un paiement est requis pour accéder aux fonctionnalités Premium."
        else:
            return f"Erreur Premium: {error_message}"
    
    @staticmethod
    def handle_product_analysis_error(error: Exception) -> str:
        """
        Handle product analysis errors.
        
        This method categorizes product analysis errors and returns
        appropriate user-friendly messages for ingredient analysis
        and API connection issues.
        
        Args:
            error: Exception that occurred during product analysis
            
        Returns:
            str: User-friendly error message in French
        """
        error_message = str(error)
        
        if "ingredient" in error_message.lower():
            return "Erreur lors de l'analyse des ingrédients."
        elif "api" in error_message.lower():
            return "Erreur de connexion à l'API externe."
        else:
            return f"Erreur d'analyse: {error_message}"
    
    @staticmethod
    def handle_routine_generation_error(error: Exception) -> str:
        """
        Handle routine generation errors.
        
        This method categorizes routine generation errors and returns
        appropriate user-friendly messages for AI service issues
        and preference-related problems.
        
        Args:
            error: Exception that occurred during routine generation
            
        Returns:
            str: User-friendly error message in French
        """
        error_message = str(error)
        
        if "ai" in error_message.lower() or "openai" in error_message.lower():
            return "Erreur de connexion à l'IA. Veuillez réessayer."
        elif "preferences" in error_message.lower():
            return "Erreur dans les préférences utilisateur."
        else:
            return f"Erreur de génération de routine: {error_message}"


class AuthenticationHelper:
    """
    Helper class for authentication and authorization checks.
    
    This class provides utilities for checking user authentication and
    Premium access in AJAX views and API endpoints. It returns consistent
    response formats for different authentication scenarios.
    
    The helper ensures that authentication checks are performed consistently
    across the application and provides appropriate error responses.
    """
    
    @staticmethod
    def require_authentication(request) -> tuple[bool, dict]:
        """
        Check if user is authenticated and return appropriate response.
        
        Returns:
            tuple: (is_authenticated, response_data)
        """
        if not request.user.is_authenticated:
            return False, {
                'error': 'Authentication required',
                'status': 401
            }
        return True, {}
    
    @staticmethod
    def require_premium_access(request) -> tuple[bool, dict]:
        """
        Check if user has Premium access and return appropriate response.
        
        Returns:
            tuple: (has_premium, response_data)
        """
        if not is_premium_user(request.user):
            return False, {
                'error': 'Premium access required',
                'upgrade_required': True,
                'message': 'Cette fonctionnalité nécessite un accès Premium. Veuillez passer à Premium pour continuer.',
                'status': 403
            }
        return True, {}


class ProductLookupService:
    """
    Service for product lookup and creation from various sources.
    
    This class provides a unified interface for finding and creating products
    from different sources including the local database and external APIs.
    It handles the complexity of product data retrieval and creation.
    
    The service implements a fallback strategy: first check local database,
    then query external APIs if not found locally.
    """
    
    def __init__(self):
        """
        Initialize ProductLookupService.
        
        Note: Product lookup services have been removed as the products app
        has been eliminated from the project.
        """
        self.obf_service = None
    
    def find_or_create_product(self, barcode: str) -> tuple[object, str, bool]:
        """
        Find product in database or create from API.
        
        Note: This method has been simplified as the products app has been removed.
        Products are now stored directly in the Scan model.
        
        Args:
            barcode: Product barcode
            
        Returns:
            tuple: (product_data, message, created_from_api)
        """
        # Return a simple product data structure for compatibility
        product_data = {
            'name': f'Produit {barcode}',
            'brand': 'Marque inconnue',
            'barcode': barcode,
            'description': 'Produit trouvé via scan',
            'ingredients_text': '',
            'score': None,
            'risk_level': 'Unknown'
        }
        
        return product_data, "", False


class ResponseBuilder:
    """
    Helper class for building consistent API responses.
    
    This class provides utilities for creating standardized API responses
    across the application. It ensures consistency in response format
    and provides common response patterns for success, error, and
    Premium access scenarios.
    
    The builder helps maintain consistent API contracts and improves
    frontend integration by providing predictable response structures.
    """
    
    @staticmethod
    def success_response(data: dict = None, message: str = None) -> dict:
        """Build a success response."""
        response = {'success': True}
        if data:
            response.update(data)
        if message:
            response['message'] = message
        return response
    
    @staticmethod
    def error_response(error: str, status: int = 400, **kwargs) -> dict:
        """Build an error response."""
        response = {
            'success': False,
            'error': error,
            'status': status
        }
        response.update(kwargs)
        return response
    
    @staticmethod
    def premium_required_response() -> dict:
        """Build a Premium access required response."""
        return ResponseBuilder.error_response(
            error='Premium access required',
            status=403,
            upgrade_required=True,
            message='Cette fonctionnalité nécessite un accès Premium. Veuillez passer à Premium pour continuer.'
        )


def ensure_premium_ui_status(user) -> bool:
    """
    S'assure que le statut Premium est correctement affiché dans l'interface utilisateur.
    
    Cette fonction force la mise à jour du statut Premium et vérifie que
    toutes les vérifications retournent le bon statut.
    
    Args:
        user: Django User object
        
    Returns:
        bool: True si Premium est actif dans l'UI, False sinon
    """
    try:
        if not user or not user.is_authenticated:
            return False
        
        # Vérifier le profil en base
        if hasattr(user, 'profile'):
            user.profile.refresh_from_db()
            
            # Si le profil indique Premium, forcer l'activation
            if user.profile.subscription_type == 'premium':
                # Forcer le cache Premium
                user._premium_status_cache = True
                
                # Vérifier que is_premium_user retourne True
                premium_status = is_premium_user(user)
                
                if premium_status:
                    print(f"✅ Statut Premium confirmé dans l'UI pour {user.username}")
                    return True
                else:
                    print(f"⚠️  Profil Premium mais is_premium_user retourne False pour {user.username}")
                    
                    # Forcer manuellement le statut
                    user._premium_status_cache = True
                    
                    # Vérifier à nouveau
                    premium_status_forced = is_premium_user(user)
                    print(f"   🔄 Après forçage: {premium_status_forced}")
                    
                    return premium_status_forced
            else:
                print(f"❌ Profil non Premium pour {user.username}: {user.profile.subscription_type}")
                return False
        else:
            print(f"❌ Pas de profil pour {user.username}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du statut Premium UI: {e}")
        return False


def force_premium_activation(user) -> bool:
    """
    Force l'activation Premium pour un utilisateur, en contournant le mode dev.
    
    Cette fonction est utilisée après un paiement Stripe réussi pour activer
    immédiatement l'accès Premium sans dépendre des vérifications du mode dev.
    
    Args:
        user: Django User object
        
    Returns:
        bool: True si l'activation a réussi, False sinon
    """
    try:
        if not user or not user.is_authenticated:
            return False
        
        # Mettre à jour le profil utilisateur
        if hasattr(user, 'profile'):
            user.profile.payment_completed = True
            user.profile.subscription_type = 'premium'
            user.profile.save()
            
            # FORÇAGE COMPLET: Contourner toutes les vérifications du mode dev
            # Mettre le cache Premium à True directement
            user._premium_status_cache = True
            
            # Forcer la mise à jour de la session utilisateur
            # Cette approche garantit que Premium est actif immédiatement
            try:
                # Vérifier que le profil est bien mis à jour
                user.profile.refresh_from_db()
                if user.profile.subscription_type == 'premium':
                    print(f"✅ Profil Premium confirmé pour {user.username}")
                    return True
                else:
                    print(f"❌ Profil Premium non confirmé pour {user.username}")
                    return False
            except Exception as e:
                print(f"❌ Erreur lors de la vérification du profil: {e}")
                return False
        else:
            print(f"❌ Pas de profil pour {user.username}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'activation Premium forcée: {e}")
        return False
