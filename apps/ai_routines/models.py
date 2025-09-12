"""
Models for AI routines functionality.
"""

from django.db import models
from django.contrib.auth.models import User


class SkinCondition(models.Model):
    """Skin conditions and concerns."""
    
    CONDITION_CHOICES = [
        ('', 'Non spécifié'),
        ('acne', 'Acné'),
        ('aging', 'Vieillissement'),
        ('dryness', 'Sécheresse'),
        ('oiliness', 'Grasse'),
        ('sensitivity', 'Sensibilité'),
        ('hyperpigmentation', 'Hyperpigmentation'),
        ('rosacea', 'Rosacée'),
        ('eczema', 'Eczéma'),
        ('combination', 'Mixte'),
        ('normal', 'Normal'),
    ]
    
    name = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_name_display()


class Routine(models.Model):
    """Personalized skincare routines."""
    
    ROUTINE_TYPE_CHOICES = [
        ('morning', 'Morning'),
        ('evening', 'Evening'),
        ('weekly', 'Weekly'),
        ('custom', 'Custom'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    name = models.CharField(max_length=100)
    routine_type = models.CharField(max_length=20, choices=ROUTINE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    steps = models.JSONField(default=list, help_text='List of routine steps')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class UserRoutineLog(models.Model):
    """Log of user routine usage."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routine_logs')
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='logs')
    completed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.routine.name} - {self.completed_at.date()}"



