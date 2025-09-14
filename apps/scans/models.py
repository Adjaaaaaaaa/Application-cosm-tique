"""
Models for product scanning functionality.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Any, Optional


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


class ProductCache(models.Model):
    """Cache for product analysis results to improve performance."""
    
    DATA_TYPE_CHOICES = [
        ('complete_analysis', 'Complete Analysis'),
        ('product_info', 'Product Information'),
        ('ai_analysis', 'AI Analysis'),
        ('safety_score', 'Safety Score'),
        ('ingredient_analysis', 'Ingredient Analysis'),
        ('barcode_lookup', 'Barcode Lookup'),
    ]
    
    cache_key = models.CharField(max_length=255, unique=True, db_index=True)
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    cached_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    access_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_accessed']
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['data_type']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.data_type} - {self.cache_key} - {self.expires_at}"
    
    @classmethod
    def get_cached_data(cls, cache_key: str, data_type: str) -> Optional[Dict[str, Any]]:
        """Get cached data if not expired."""
        try:
            cache_entry = cls.objects.get(cache_key=cache_key, data_type=data_type)
            
            # Check if expired
            if cache_entry.expires_at <= timezone.now():
                cache_entry.delete()
                return None
            
            # Update access statistics
            cache_entry.access_count += 1
            cache_entry.save(update_fields=['access_count', 'last_accessed'])
            
            return cache_entry.cached_data
            
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_cached_data(cls, cache_key: str, data: Dict[str, Any], data_type: str, ttl_hours: int) -> None:
        """Set cached data with TTL."""
        expires_at = timezone.now() + timedelta(hours=ttl_hours)
        
        cache_entry, created = cls.objects.update_or_create(
            cache_key=cache_key,
            data_type=data_type,
            defaults={
                'cached_data': data,
                'expires_at': expires_at,
                'access_count': 0,
            }
        )
    
    @classmethod
    def clear_expired_cache(cls) -> int:
        """Clear all expired cache entries."""
        expired_count = cls.objects.filter(expires_at__lte=timezone.now()).count()
        cls.objects.filter(expires_at__lte=timezone.now()).delete()
        return expired_count
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = cls.objects.count()
        active_entries = cls.objects.filter(expires_at__gt=timezone.now()).count()
        expired_entries = total_entries - active_entries
        
        return {
            'total_entries': total_entries,
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'hit_rate': 0.0,  # Could be calculated from access_count
        }


