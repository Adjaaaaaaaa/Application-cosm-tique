"""
Views for user authentication and profile management.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .forms import CustomUserCreationForm

from .forms import UserProfileForm, AllergyForm
from .models import UserProfile, Allergy
from common.premium_utils import force_premium_status_update
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.conf import settings




def home_view(request):
    """Enhanced home view with product scanning functionality."""
    # Handle downgrade notification
    downgraded_user_id = request.GET.get('downgraded')
    if downgraded_user_id and request.user.is_authenticated:
        # Force update Premium status to ensure UI reflects changes immediately
        force_premium_status_update(request.user)
        
        # Add context to indicate downgrade just happened
        context = {
            'just_downgraded': True,
            'downgrade_message': 'Votre abonnement Premium a été annulé avec succès. Vous avez maintenant accès aux fonctionnalités gratuites.'
        }
        return render(request, 'accounts/home.html', context)
    
    return render(request, 'accounts/home.html')


def signup_view(request):
    """Inscription avec email obligatoire."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, 'Inscription réussie ! Bienvenue sur BeautyScan.')
            return redirect('accounts:home')
        else:
            # Afficher les erreurs spécifiques
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    """Connexion via nom d'utilisateur ou email + mot de passe."""
    if request.method == 'POST':
        identifier = request.POST.get('email') or request.POST.get('username')
        password = request.POST.get('password')
        
        if not identifier:
            messages.error(request, "Veuillez saisir votre nom d'utilisateur ou votre adresse email.")
            return render(request, 'accounts/login.html')
        
        if not password:
            messages.error(request, "Veuillez saisir votre mot de passe.")
            return render(request, 'accounts/login.html')
        
        user = None
        if '@' in identifier:
            # Connexion par email
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                if not user_obj.is_active:
                    messages.error(request, "Votre compte n'est pas encore activé.")
                    return render(request, 'accounts/login.html')
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            # Connexion par nom d'utilisateur
            try:
                user_obj = User.objects.get(username=identifier)
                if not user_obj.is_active:
                    messages.error(request, "Votre compte n'est pas encore activé.")
                    return render(request, 'accounts/login.html')
                user = authenticate(request, username=identifier, password=password)
            except User.DoesNotExist:
                user = None
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Connexion réussie !')
            return redirect(request.GET.get('next', 'accounts:home'))
        else:
            messages.error(request, "Nom d'utilisateur/email ou mot de passe incorrect.")
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'Déconnexion réussie')
    return redirect('accounts:home')


def verify_email_view(request):
    """Validation de l'email à partir du lien reçu par email."""
    uid = request.GET.get('uid')
    token = request.GET.get('token')
    if not uid or not token:
        messages.error(request, "Lien de validation invalide.")
        return redirect('accounts:login')
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        signer = TimestampSigner()
        # Jeton valable 48h
        unsigned = signer.unsign(token, max_age=60*60*48)
        if str(unsigned) != str(user_id):
            raise BadSignature('uid mismatch')
        user = User.objects.get(pk=user_id)
        user.is_active = True
        user.save()
        messages.success(request, "Votre adresse email a été validée. Vous pouvez vous connecter.")
        return redirect('accounts:login')
    except (User.DoesNotExist, BadSignature, SignatureExpired, ValueError):
        messages.error(request, "Lien de validation invalide ou expiré.")
        return redirect('accounts:signup')


@login_required
def profile_view(request):
    """
    User profile view with improved data persistence.
    
    ✅ CORRECTION CRITIQUE : Les champs multi-choice (JSON) sont maintenant toujours initialisés
    avec une liste (même vide) pour que les cases cochées restent fixées après sauvegarde.
    
    Champs concernés :
    - skin_concerns (multi-choice)
    - dermatological_conditions (multi-choice) 
    - allergies (multi-choice)
    - objectives (multi-choice)
    """
    # ✅ Logger défini au début pour toute la fonction
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create profile as fallback if missing
        logger.warning(f"UserProfile missing for user {request.user.id}, creating fallback")
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            try:
                # Update User model fields
                user = request.user
                user.first_name = form.cleaned_data.get('first_name', '')
                user.last_name = form.cleaned_data.get('last_name', '')
                user.email = form.cleaned_data.get('email', '')
                user.save()
                
                # Update profile with form data
                profile = form.save(commit=False)
                
                # ✅ JSON fields - toujours traiter même si liste vide
                skin_concerns_data = form.cleaned_data.get('skin_concerns', [])
                dermatological_conditions_data = form.cleaned_data.get('dermatological_conditions', [])
                allergies_data = form.cleaned_data.get('allergies', [])
                objectives_data = form.cleaned_data.get('objectives', [])
                
                # Sauvegarder les listes JSON (même vides) pour persistance
                profile.set_skin_concerns_list(skin_concerns_data)
                profile.set_dermatological_conditions_list(dermatological_conditions_data)
                profile.set_allergies_list(allergies_data)
                profile.set_objectives_list(objectives_data)
                
                # ✅ Single choice fields - toujours mettre à jour
                profile.skin_type = form.cleaned_data.get('skin_type') or profile.skin_type
                profile.age_range = form.cleaned_data.get('age_range') or profile.age_range
                profile.product_style = form.cleaned_data.get('product_style') or profile.product_style
                profile.routine_frequency = form.cleaned_data.get('routine_frequency') or profile.routine_frequency
                profile.budget = form.cleaned_data.get('budget') or profile.budget
                
                # ✅ Text fields - toujours mettre à jour
                profile.dermatological_other = form.cleaned_data.get('dermatological_other', '')
                profile.allergies_other = form.cleaned_data.get('allergies_other', '')
                
                # Sauvegarder le profil AVANT de continuer
                profile.save()
                
                # Log pour debug
                logger.info(f"Profile saved successfully for user {request.user.id}")
                logger.info(f"Skin concerns: {profile.get_skin_concerns_list()}")
                logger.info(f"Allergies: {profile.get_allergies_list()}")
                logger.info(f"Dermatological conditions: {profile.get_dermatological_conditions_list()}")
                logger.info(f"Objectives: {profile.get_objectives_list()}")
                return redirect('accounts:profile')
                
            except Exception as e:
                logger.error(f"Profile save error for user {request.user.id}: {e}")
        else:
            # Handle form validation errors
            _handle_form_errors(form, request)
    else:
        form = UserProfileForm(instance=profile)
    
    # Pre-populate User fields (done once)
    _prepopulate_user_fields(form, request.user)
    
    # Pre-populate Profile fields
    _prepopulate_profile_fields(form, profile)
    
    allergies = Allergy.objects.filter(user=request.user)
    
    # Passer les valeurs initiales au template pour l'affichage
    initial_values = {
        'skin_concerns': profile.get_skin_concerns_list() or [],
        'allergies': profile.get_allergies_list() or [],
        'dermatological_conditions': profile.get_dermatological_conditions_list() or [],
        'objectives': profile.get_objectives_list() or [],
    }
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'allergies': allergies,
        'initial_values': initial_values
    })


def _prepopulate_user_fields(form, user):
    """Helper function to pre-populate User model fields in the form."""
    form.fields['first_name'].initial = user.first_name
    form.fields['last_name'].initial = user.last_name
    form.fields['email'].initial = user.email


def _prepopulate_profile_fields(form, profile):
    """
    Helper function to pre-populate Profile model fields in the form.
    
    ✅ CORRECTION CRITIQUE : Les champs multi-choice sont toujours initialisés avec une liste
    (même vide) pour éviter la perte des sélections après sauvegarde.
    
    Cette fonction garantit que :
    1. Les champs multi-choice ont toujours une liste (même vide)
    2. Les champs simples ont une valeur explicite (même None)
    3. Les champs texte ont une chaîne explicite (même vide)
    """
    # ✅ Single choice fields - toujours assigner une valeur (même None)
    form.fields['skin_type'].initial = profile.skin_type or None
    form.fields['age_range'].initial = profile.age_range or None
    form.fields['product_style'].initial = profile.product_style or None
    form.fields['routine_frequency'].initial = profile.routine_frequency or None
    form.fields['budget'].initial = profile.budget or None
    
    # ✅ Text fields - toujours assigner une chaîne (même vide)
    form.fields['dermatological_other'].initial = profile.dermatological_other or ''
    form.fields['allergies_other'].initial = profile.allergies_other or ''
    
    # ✅ Multi-choice fields — toujours assigner une liste (même vide)
    form.fields['skin_concerns'].initial = profile.get_skin_concerns_list() or []
    form.fields['dermatological_conditions'].initial = profile.get_dermatological_conditions_list() or []
    form.fields['allergies'].initial = profile.get_allergies_list() or []
    form.fields['objectives'].initial = profile.get_objectives_list() or []


def _handle_form_errors(form, request):
    """Helper function to handle and display form validation errors."""
    for field_name, errors in form.errors.items():
        for error in errors:
            # Get field label in French
            field_label = form.fields[field_name].label if field_name in form.fields else field_name
            messages.error(request, f"{field_label}: {error}")


@login_required
def add_allergy_view(request):
    """Add allergy view with improved error handling."""
    if request.method == 'POST':
        form = AllergyForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                allergy = form.save(commit=False)
                allergy.user = request.user
                allergy.save()
                return redirect('accounts:profile')
            except Exception as e:
                logger.error(f'Error adding allergy: {str(e)}')
        else:
            _handle_form_errors(form, request)
    else:
        form = AllergyForm(user=request.user)
    
    return render(request, 'accounts/add_allergy.html', {'form': form})


@login_required
def delete_allergy_view(request, allergy_id):
    """Delete allergy view with improved error handling."""
    try:
        allergy = Allergy.objects.get(id=allergy_id, user=request.user)
        allergy_name = allergy.ingredient_name
        allergy.delete()
    except Allergy.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f'Error deleting allergy: {str(e)}')
    
    return redirect('accounts:profile')


@login_required
def delete_account(request):
    """
    Vue pour supprimer définitivement le compte utilisateur.
    Cette action est irréversible et supprime toutes les données associées.
    """
    if request.method != 'POST':
        messages.error(request, 'Méthode non autorisée.')
        return redirect('accounts:profile')
    
    try:
        with transaction.atomic():
            user = request.user
            
            # Supprimer le profil utilisateur (cela supprimera aussi les allergies)
            try:
                profile = UserProfile.objects.get(user=user)
                profile.delete()
            except UserProfile.DoesNotExist:
                pass
            
            # Supprimer toutes les données associées à l'utilisateur
            # Scans
            from apps.scans.models import Scan
            Scan.objects.filter(user=user).delete()
            
            # Routines IA
            from apps.ai_routines.models import AIRoutine
            AIRoutine.objects.filter(user=user).delete()
            
            # Messages de chat
            from apps.ai_routines.models import ChatMessage
            ChatMessage.objects.filter(user=user).delete()
            
            # Déconnexion avant suppression
            logout(request)
            
            # Supprimer l'utilisateur (cela supprimera aussi les allergies via CASCADE)
            user.delete()
            
            messages.success(request, 'Votre compte a été supprimé avec succès. Nous sommes désolés de vous voir partir.')
            return redirect('accounts:login')
            
    except Exception as e:
        messages.error(request, f'Une erreur est survenue lors de la suppression du compte: {str(e)}')
        return redirect('accounts:profile')


def privacy_policy_view(request):
    """
    Vue pour afficher la politique de confidentialité de BeautyScan.
    """
    return render(request, 'accounts/privacy_policy.html')


def terms_of_service_view(request):
    """
    Vue pour afficher les conditions d'utilisation de BeautyScan.
    """
    return render(request, 'accounts/terms_of_service.html')




