"""
Models for user accounts, profiles, and allergies.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with skincare preferences."""
    
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
    ]
    
    SKIN_TYPE_CHOICES = [
        ('', 'Non spécifié'),
        ('normal', 'Normal'),
        ('dry', 'Sèche'),
        ('oily', 'Grasse'),
        ('combination', 'Mixte'),
        ('sensitive', 'Sensible'),
    ]
    
    BUDGET_CHOICES = [
        ('low', 'Low (< 50€/month)'),
        ('moderate', 'Moderate (50-150€/month)'),
        ('high', 'High (> 150€/month)'),
    ]
    
    AGE_RANGE_CHOICES = [
        ('under18', 'Moins de 18 ans'),
        ('18-25', '18–25 ans'),
        ('26-35', '26–35 ans'),
        ('36-45', '36–45 ans'),
        ('46-60', '46–60 ans'),
        ('60plus', '60+ ans'),
    ]
    
    ROUTINE_TYPE_CHOICES = [
        ('morning', 'Matin'),
        ('evening', 'Soir'),
        ('custom', 'Personnalisée'),
    ]
    
    PRODUCT_STYLE_CHOICES = [
        ('natural', 'Bio / Naturel'),
        ('pharmacy', 'Pharmacie / Dermatologique'),
        ('luxury', 'Luxe / Haut de gamme'),
        ('minimalist', 'Minimaliste'),
    ]
    
    ROUTINE_FREQUENCY_CHOICES = [
        ('quick', 'Rapide (≤ 5 min)'),
        ('standard', 'Standard (10–20 min)'),
        ('comprehensive', 'Complète (20–30 min)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    subscription_type = models.CharField(
        max_length=10, 
        choices=SUBSCRIPTION_CHOICES, 
        default='free'
    )
    
    # Routine preferences (transferred from generate_routine form)
    routine_type = models.CharField(
        max_length=20, 
        choices=ROUTINE_TYPE_CHOICES, 
        default='morning',
        help_text='Type de routine préféré'
    )
    skin_type = models.CharField(max_length=50, blank=True, choices=SKIN_TYPE_CHOICES, default='')
    skin_concerns = models.TextField(blank=True, help_text='Problèmes de peau (JSON format)')
    age_range = models.CharField(max_length=10, blank=True, choices=AGE_RANGE_CHOICES)
    dermatological_conditions = models.TextField(blank=True, help_text='Pathologies dermatologiques (JSON format)')
    dermatological_other = models.CharField(max_length=200, blank=True, help_text='Autre pathologie dermatologique')
    allergies = models.TextField(blank=True, help_text='Allergies connues (JSON format)')
    allergies_other = models.CharField(max_length=200, blank=True, help_text='Autre allergie')
    product_style = models.CharField(max_length=20, blank=True, choices=PRODUCT_STYLE_CHOICES)
    routine_frequency = models.CharField(max_length=20, blank=True, choices=ROUTINE_FREQUENCY_CHOICES)
    objectives = models.TextField(blank=True, help_text='Objectifs principaux (JSON format)')
    
    # Legacy fields (kept for compatibility)
    budget = models.CharField(max_length=20, blank=True, choices=BUDGET_CHOICES)
    pathologies = models.TextField(blank=True, help_text='Any skin conditions or medical concerns')
    payment_completed = models.BooleanField(default=False, help_text='Whether payment was completed for Premium upgrade')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def is_premium(self) -> bool:
        """
        Check if user has Premium access.
        
        This method uses the premium_utils module to handle both
        production subscription checks and developer testing mode.
        """
        from common.premium_utils import is_premium_user
        return is_premium_user(self.user)
    
    def get_skin_concerns_list(self) -> list:
        """Get skin concerns as a list from JSON field."""
        import json
        try:
            return json.loads(self.skin_concerns) if self.skin_concerns else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_skin_concerns_list(self, concerns_list: list):
        """Set skin concerns as JSON from list."""
        import json
        self.skin_concerns = json.dumps(concerns_list) if concerns_list else ''
    
    def get_dermatological_conditions_list(self) -> list:
        """Get dermatological conditions as a list from JSON field."""
        import json
        try:
            return json.loads(self.dermatological_conditions) if self.dermatological_conditions else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_dermatological_conditions_list(self, conditions_list: list):
        """Set dermatological conditions as JSON from list."""
        import json
        self.dermatological_conditions = json.dumps(conditions_list) if conditions_list else ''
    
    def get_allergies_list(self) -> list:
        """Get allergies as a list from JSON field."""
        import json
        try:
            return json.loads(self.allergies) if self.allergies else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_allergies_list(self, allergies_list: list):
        """Set allergies as JSON from list."""
        import json
        self.allergies = json.dumps(allergies_list) if allergies_list else ''
    
    def get_objectives_list(self) -> list:
        """Get objectives as a list from JSON field."""
        import json
        try:
            return json.loads(self.objectives) if self.objectives else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_objectives_list(self, objectives_list: list):
        """Set objectives as JSON from list."""
        import json
        self.objectives = json.dumps(objectives_list) if objectives_list else ''


class Allergy(models.Model):
    """User allergies and sensitivities."""
    
    SEVERITY_CHOICES = [
        ('mild', 'Légère'),
        ('moderate', 'Modérée'),
        ('severe', 'Sévère'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='allergies')
    ingredient_name = models.CharField(max_length=200)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='mild')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Allergies'
        unique_together = ['user', 'ingredient_name']
    
    def __str__(self):
        return f"{self.user.username} - {self.ingredient_name}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when a new user is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved."""
    instance.profile.save()
