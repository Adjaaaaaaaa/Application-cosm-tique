"""
Forms for user registration and profile management.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Allergy


class CustomUserCreationForm(UserCreationForm):
    """
    Formulaire d'inscription personnalisé avec email obligatoire.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-custom',
            'placeholder': 'Choisissez votre nom d\'utilisateur',
            'autocomplete': 'username'
        }),
        label='Nom d\'utilisateur',
        help_text='Choisissez un nom d\'utilisateur unique (3-30 caractères)'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-custom',
            'placeholder': 'votre.email@exemple.com',
            'autocomplete': 'email'
        }),
        label='Adresse email *',
        help_text='L\'adresse email est obligatoire pour l\'inscription.'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-custom',
            'placeholder': 'Créez un mot de passe fort',
            'autocomplete': 'new-password'
        }),
        label='Mot de passe',
        help_text='Minimum 8 caractères avec majuscules, minuscules et chiffres'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-custom',
            'placeholder': 'Confirmez votre mot de passe',
            'autocomplete': 'new-password'
        }),
        label='Confirmer le mot de passe',
        help_text='Répétez votre mot de passe pour confirmation'
    )
    
    accept_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='J\'accepte les conditions d\'utilisation et la politique de confidentialité',
        help_text='Vous devez accepter nos conditions pour créer un compte.',
        error_messages={
            'required': 'Vous devez accepter les conditions d\'utilisation et la politique de confidentialité pour créer un compte.'
        }
    )
    
    def clean_username(self):
        """Validation personnalisée du nom d'utilisateur."""
        username = self.cleaned_data.get('username')
        if username:
            if len(username) < 3:
                raise forms.ValidationError('Le nom d\'utilisateur doit contenir au moins 3 caractères.')
            if not username.replace('_', '').replace('-', '').isalnum():
                raise forms.ValidationError('Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores.')
        return username
    
    def clean_password1(self):
        """Validation personnalisée du mot de passe."""
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise forms.ValidationError('Le mot de passe doit contenir au moins 8 caractères.')
            if not any(c.isupper() for c in password1):
                raise forms.ValidationError('Le mot de passe doit contenir au moins une majuscule.')
            if not any(c.islower() for c in password1):
                raise forms.ValidationError('Le mot de passe doit contenir au moins une minuscule.')
            if not any(c.isdigit() for c in password1):
                raise forms.ValidationError('Le mot de passe doit contenir au moins un chiffre.')
        return password1
    
    def clean_accept_terms(self):
        """Vérifier que l'utilisateur a accepté les conditions."""
        accept_terms = self.cleaned_data.get('accept_terms')
        if not accept_terms:
            raise forms.ValidationError(
                'Vous devez accepter les conditions d\'utilisation et la politique de confidentialité pour créer un compte.'
            )
        return accept_terms
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        """Vérifier que l'email est unique."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'Cette adresse email est déjà utilisée par un autre compte.'
            )
        return email
    
    def save(self, commit=True):
        """Sauvegarder l'utilisateur avec l'email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile with all routine preferences."""
    
    # User fields (from Django User model) - these are not part of UserProfile
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre prénom'}),
        label='Prénom'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom'}),
        label='Nom'
    )
    
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre.email@exemple.com'}),
        label='Adresse email'
    )
    
    # Skin type selection
    skin_type = forms.ChoiceField(
        choices=UserProfile.SKIN_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label='Type de peau'
    )
    
    # Age range selection
    age_range = forms.ChoiceField(
        choices=UserProfile.AGE_RANGE_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label='Tranche d\'âge'
    )
    
    # Skin concerns (multiple choice)
    skin_concerns = forms.MultipleChoiceField(
        choices=[
            ('acne', 'Acné'),
            ('aging', 'Vieillissement'),
            ('dryness', 'Sécheresse'),
            ('oiliness', 'Excès de sébum'),
            ('sensitivity', 'Sensibilité'),
            ('hyperpigmentation', 'Taches'),
            ('texture', 'Texture'),
            ('pores', 'Pores dilatés'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Problèmes de peau'
    )
    
    # Dermatological conditions
    dermatological_conditions = forms.MultipleChoiceField(
        choices=[
            ('eczema', 'Eczéma'),
            ('psoriasis', 'Psoriasis'),
            ('rosacea', 'Rosacée'),
            ('seborrheic_dermatitis', 'Dermatite séborrhéique'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Pathologies dermatologiques connues'
    )
    
    dermatological_other = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Autre (précisez)'}),
        label='Autre pathologie'
    )
    
    # Allergies
    allergies = forms.MultipleChoiceField(
        choices=[
            ('fragrance', 'Parfum'),
            ('essential_oils', 'Huiles essentielles'),
            ('preservatives', 'Conservateurs'),
            ('nickel_metals', 'Nickel / métaux'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Allergies connues'
    )
    
    allergies_other = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Autre (précisez)'}),
        label='Autre allergie'
    )
    
    # Product style preference
    product_style = forms.ChoiceField(
        choices=UserProfile.PRODUCT_STYLE_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label='Style de produits préféré'
    )
    
    # Routine frequency
    routine_frequency = forms.ChoiceField(
        choices=UserProfile.ROUTINE_FREQUENCY_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label='Fréquence souhaitée de la routine'
    )
    
    # Objectives (multiple choice)
    objectives = forms.MultipleChoiceField(
        choices=[
            ('anti-âge', 'Anti-âge'),
            ('traitement acné', 'Traitement de l\'acné'),
            ('hydratation', 'Hydratation'),
            ('éclat', 'Éclat du teint'),
            ('raffermissement', 'Raffermissement'),
            ('apaisement', 'Apaisement'),
            ('protection solaire', 'Protection solaire'),
            ('exfoliation', 'Exfoliation'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Objectifs principaux'
    )
    

    
    # Budget (legacy field)
    budget = forms.ChoiceField(
        choices=UserProfile.BUDGET_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        label='Budget mensuel'
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'skin_type', 'age_range', 'skin_concerns',
            'dermatological_conditions', 'dermatological_other',
            'allergies', 'allergies_other', 'product_style',
            'routine_frequency', 'objectives', 'budget'
        ]
        widgets = {
            'skin_type': forms.RadioSelect,
            'age_range': forms.RadioSelect,
            'product_style': forms.RadioSelect,
            'routine_frequency': forms.RadioSelect,
            'budget': forms.RadioSelect,
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Pre-populate multiple choice fields from JSON data
            if self.instance.skin_concerns:
                skin_concerns_list = self.instance.get_skin_concerns_list()
                self.fields['skin_concerns'].initial = skin_concerns_list
            
            if self.instance.dermatological_conditions:
                dermatological_conditions_list = self.instance.get_dermatological_conditions_list()
                self.fields['dermatological_conditions'].initial = dermatological_conditions_list
            
            if self.instance.allergies:
                allergies_list = self.instance.get_allergies_list()
                self.fields['allergies'].initial = allergies_list
            
            if self.instance.objectives:
                objectives_list = self.instance.get_objectives_list()
                self.fields['objectives'].initial = objectives_list
            
            # Pre-populate single choice fields
            if self.instance.skin_type:
                self.fields['skin_type'].initial = self.instance.skin_type
            
            if self.instance.age_range:
                self.fields['age_range'].initial = self.instance.age_range
            
            if self.instance.product_style:
                self.fields['product_style'].initial = self.instance.product_style
            
            if self.instance.routine_frequency:
                self.fields['routine_frequency'].initial = self.instance.routine_frequency
            
            if self.instance.budget:
                self.fields['budget'].initial = self.instance.budget
            
            # Pre-populate text fields
            if self.instance.dermatological_other:
                self.fields['dermatological_other'].initial = self.instance.dermatological_other
            
            if self.instance.allergies_other:
                self.fields['allergies_other'].initial = self.instance.allergies_other


class AllergyForm(forms.ModelForm):
    """Form for adding/editing allergies."""
    
    class Meta:
        model = Allergy
        fields = ['ingredient_name', 'severity', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_ingredient_name(self):
        """Ensure ingredient name is unique for the user."""
        ingredient_name = self.cleaned_data.get('ingredient_name')
        if self.user and Allergy.objects.filter(
            user=self.user, 
            ingredient_name__iexact=ingredient_name
        ).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError('This allergy is already registered.')
        return ingredient_name
