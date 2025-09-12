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
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@exemple.com'
        }),
        label='Adresse email *',
        help_text='L\'adresse email est obligatoire pour l\'inscription.'
    )
    
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
            ('anti_aging', 'Anti-âge'),
            ('acne_treatment', 'Traitement de l\'acné'),
            ('hydration', 'Hydratation'),
            ('brightening', 'Éclat du teint'),
            ('firming', 'Raffermissement'),
            ('soothing', 'Apaisement'),
            ('protection', 'Protection solaire'),
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
