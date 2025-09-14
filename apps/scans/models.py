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


class ProductCache(models.Model):
    """
    Cache model for storing product analysis results to optimize performance.
    
    This model stores various types of cached data with different TTL (Time To Live)
    to avoid repeated API calls and improve response times.
    """
    
    DATA_TYPE_CHOICES = [
        ('product_info', 'Product Information'),
        ('ingredient_analysis', 'Ingredient Analysis'),
        ('barcode_lookup', 'Barcode Lookup'),
        ('ai_analysis', 'AI Analysis'),
        ('safety_score', 'Safety Score'),
        ('complete_analysis', 'Complete Analysis'),
    ]
    
    cache_key = models.CharField(
        max_length=255, 
        unique=True, 
        db_index=True,
        help_text="Unique cache key for the stored data"
    )
    data = models.JSONField(
        help_text="Cached data in JSON format"
    )
    data_type = models.CharField(
        max_length=50, 
        choices=DATA_TYPE_CHOICES,
        help_text="Type of cached data"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the cache entry was created"
    )
    expires_at = models.DateTimeField(
        help_text="When the cache entry expires"
    )
    access_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this cache entry has been accessed"
    )
    last_accessed = models.DateTimeField(
        auto_now=True,
        help_text="Last time this cache entry was accessed"
    )
    
    class Meta:
        ordering = ['-last_accessed']
        indexes = [
            models.Index(fields=['cache_key'], name='scans_produ_cache_k_9eac0a_idx'),
            models.Index(fields=['data_type'], name='scans_produ_data_ty_daa4c3_idx'),
            models.Index(fields=['expires_at'], name='scans_produ_expires_4b9395_idx'),
        ]
        verbose_name = "Product Cache"
        verbose_name_plural = "Product Caches"
    
    def __str__(self):
        return f"{self.data_type} - {self.cache_key} (expires: {self.expires_at})"
    
    @classmethod
    def get_cached_data(cls, cache_key: str, data_type: str):
        """
        Retrieve cached data if it exists and hasn't expired.
        
        Args:
            cache_key: The cache key to look for
            data_type: The type of data to retrieve
            
        Returns:
            Cached data if found and not expired, None otherwise
        """
        try:
            cache_entry = cls.objects.get(
                cache_key=cache_key,
                data_type=data_type,
                expires_at__gt=timezone.now()
            )
            
            # Update access statistics
            cache_entry.access_count += 1
            cache_entry.save(update_fields=['access_count', 'last_accessed'])
            
            return cache_entry.data
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_cached_data(cls, cache_key: str, data: dict, data_type: str, ttl_hours: int):
        """
        Store data in cache with specified TTL.
        
        Args:
            cache_key: Unique key for the cache entry
            data: Data to cache
            data_type: Type of data being cached
            ttl_hours: Time to live in hours
        """
        expires_at = timezone.now() + timedelta(hours=ttl_hours)
        
        cache_entry, created = cls.objects.update_or_create(
            cache_key=cache_key,
            data_type=data_type,
            defaults={
                'data': data,
                'expires_at': expires_at,
                'access_count': 0,
            }
        )
        
        return cache_entry
    
    @classmethod
    def clear_expired_cache(cls):
        """
        Remove all expired cache entries.
        
        Returns:
            Number of entries deleted
        """
        expired_count = cls.objects.filter(
            expires_at__lt=timezone.now()
        ).count()
        
        cls.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        
        return expired_count
    
    @classmethod
    def get_cache_stats(cls):
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        now = timezone.now()
        total_entries = cls.objects.count()
        active_entries = cls.objects.filter(expires_at__gt=now).count()
        expired_entries = total_entries - active_entries
        
        total_access = cls.objects.aggregate(
            total=models.Sum('access_count')
        )['total'] or 0
        
        return {
            'total_entries': total_entries,
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'total_access': total_access,
        }


