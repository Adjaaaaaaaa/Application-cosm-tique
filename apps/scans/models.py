"""
Models for product scanning functionality.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Scan(models.Model):
    """Product scan record with embedded product information."""
    
    SCAN_TYPE_CHOICES = [
        ('barcode', 'Barcode Scan'),
        ('image', 'Image Upload'),
        ('manual', 'Manual Entry'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scans')
    scan_type = models.CharField(max_length=10, choices=SCAN_TYPE_CHOICES)
    barcode = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='scans/', blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    # Embedded product information (replaces Product model dependency)
    product_name = models.CharField(max_length=200, blank=True)
    product_brand = models.CharField(max_length=100, blank=True)
    product_description = models.TextField(blank=True)
    product_ingredients_text = models.TextField(blank=True)
    product_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    product_risk_level = models.CharField(max_length=20, blank=True)
    analysis_available = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-scanned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.product_name or 'Unknown Product'} - {self.scanned_at.date()}"
    
    @property
    def product(self):
        """Return product information as a dict for compatibility."""
        return {
            'name': self.product_name,
            'brand': self.product_brand,
            'description': self.product_description,
            'ingredients_text': self.product_ingredients_text,
            'score': self.product_score,
            'risk_level': self.product_risk_level,
        }


