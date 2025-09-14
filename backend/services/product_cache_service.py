"""
Cache service to optimize product analysis performance.

This service manages an intelligent cache that stores analysis results
to avoid repeated calls to external APIs.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import timedelta
from django.utils import timezone
from apps.scans.models import ProductCache

logger = logging.getLogger(__name__)


class ProductCacheService:
    """
    Cache service for product analyses.
    
    Manages an intelligent cache with different strategies based on data type:
    - Product information: 24h
    - AI analyses: 12h  
    - Safety scores: 48h
    - Complete analyses: 6h
    """
    
    # Cache durations by data type (in hours)
    CACHE_TTL = {
        'product_info': 24,        # Product information: 24h
        'ingredient_analysis': 12,  # Ingredient analysis: 12h
        'barcode_lookup': 24,      # Barcode lookup: 24h
        'ai_analysis': 12,         # AI analysis: 12h
        'safety_score': 48,        # Safety score: 48h
        'complete_analysis': 6,    # Complete analysis: 6h
    }
    
    def __init__(self):
        """Initialize the cache service."""
        self.logger = logger
        self.logger.info("ProductCacheService initialized")
    
    def get_cached_analysis(self, barcode: str, user_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached complete analysis.
        
        Args:
            barcode: Product barcode
            user_id: User ID (optional for personalized cache)
            
        Returns:
            Cached analysis or None if not found/expired
        """
        cache_key = self._build_cache_key('complete_analysis', barcode, user_id)
        cached_data = ProductCache.get_cached_data(cache_key, 'complete_analysis')
        
        if cached_data:
            self.logger.info(f"Cache hit for complete analysis: {barcode}")
            return cached_data
        
        return None
    
    def set_cached_analysis(self, barcode: str, analysis_data: Dict[str, Any], user_id: int = None) -> None:
        """
        Cache a complete analysis.
        
        Args:
            barcode: Product barcode
            analysis_data: Analysis data to cache
            user_id: User ID (optional)
        """
        cache_key = self._build_cache_key('complete_analysis', barcode, user_id)
        ttl_hours = self.CACHE_TTL['complete_analysis']
        
        ProductCache.set_cached_data(cache_key, analysis_data, 'complete_analysis', ttl_hours)
        self.logger.info(f"Cached complete analysis: {barcode} (TTL: {ttl_hours}h)")
    
    def get_cached_product_info(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached product information.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Cached product information or None
        """
        cache_key = self._build_cache_key('product_info', barcode)
        cached_data = ProductCache.get_cached_data(cache_key, 'product_info')
        
        if cached_data:
            self.logger.info(f"Cache hit for product info: {barcode}")
            return cached_data
        
        return None
    
    def set_cached_product_info(self, barcode: str, product_data: Dict[str, Any]) -> None:
        """
        Cache product information.
        
        Args:
            barcode: Product barcode
            product_data: Product data to cache
        """
        cache_key = self._build_cache_key('product_info', barcode)
        ttl_hours = self.CACHE_TTL['product_info']
        
        ProductCache.set_cached_data(cache_key, product_data, 'product_info', ttl_hours)
        self.logger.info(f"Cached product info: {barcode} (TTL: {ttl_hours}h)")
    
    def get_cached_ai_analysis(self, barcode: str, user_id: int, question: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached AI analysis.
        
        Args:
            barcode: Product barcode
            user_id: User ID
            question: Specific question (optional)
            
        Returns:
            Cached AI analysis or None
        """
        cache_key = self._build_cache_key('ai_analysis', barcode, user_id, question)
        cached_data = ProductCache.get_cached_data(cache_key, 'ai_analysis')
        
        if cached_data:
            self.logger.info(f"Cache hit for AI analysis: {barcode} (user: {user_id})")
            return cached_data
        
        return None
    
    def set_cached_ai_analysis(self, barcode: str, user_id: int, analysis_data: Dict[str, Any], question: str = None) -> None:
        """
        Cache an AI analysis.
        
        Args:
            barcode: Product barcode
            user_id: User ID
            analysis_data: AI analysis data to cache
            question: Specific question (optional)
        """
        cache_key = self._build_cache_key('ai_analysis', barcode, user_id, question)
        ttl_hours = self.CACHE_TTL['ai_analysis']
        
        ProductCache.set_cached_data(cache_key, analysis_data, 'ai_analysis', ttl_hours)
        self.logger.info(f"Cached AI analysis: {barcode} (user: {user_id}, TTL: {ttl_hours}h)")
    
    def get_cached_safety_score(self, barcode: str, user_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached safety score.
        
        Args:
            barcode: Product barcode
            user_id: User ID (optional)
            
        Returns:
            Cached safety score or None
        """
        cache_key = self._build_cache_key('safety_score', barcode, user_id)
        cached_data = ProductCache.get_cached_data(cache_key, 'safety_score')
        
        if cached_data:
            self.logger.info(f"Cache hit for safety score: {barcode}")
            return cached_data
        
        return None
    
    def set_cached_safety_score(self, barcode: str, safety_data: Dict[str, Any], user_id: int = None) -> None:
        """
        Cache a safety score.
        
        Args:
            barcode: Product barcode
            safety_data: Safety data to cache
            user_id: User ID (optional)
        """
        cache_key = self._build_cache_key('safety_score', barcode, user_id)
        ttl_hours = self.CACHE_TTL['safety_score']
        
        ProductCache.set_cached_data(cache_key, safety_data, 'safety_score', ttl_hours)
        self.logger.info(f"Cached safety score: {barcode} (TTL: {ttl_hours}h)")
    
    def _build_cache_key(self, data_type: str, barcode: str, user_id: int = None, question: str = None) -> str:
        """
        Build a unique cache key.
        
        Args:
            data_type: Data type
            barcode: Product barcode
            user_id: User ID (optional)
            question: Specific question (optional)
            
        Returns:
            Unique cache key
        """
        key_parts = [data_type, barcode]
        
        if user_id:
            key_parts.append(f"user_{user_id}")
        
        if question:
            # Create a hash of the question to avoid keys that are too long
            import hashlib
            question_hash = hashlib.md5(question.encode()).hexdigest()[:8]
            key_parts.append(f"q_{question_hash}")
        
        return "_".join(key_parts)
    
    def clear_cache_for_product(self, barcode: str) -> int:
        """
        Remove all caches for a specific product.
        
        Args:
            barcode: Product barcode
            
        Returns:
            Number of entries deleted
        """
        deleted_count = ProductCache.objects.filter(
            cache_key__startswith=f"complete_analysis_{barcode}"
        ).delete()[0]
        
        deleted_count += ProductCache.objects.filter(
            cache_key__startswith=f"product_info_{barcode}"
        ).delete()[0]
        
        deleted_count += ProductCache.objects.filter(
            cache_key__startswith=f"ai_analysis_{barcode}"
        ).delete()[0]
        
        deleted_count += ProductCache.objects.filter(
            cache_key__startswith=f"safety_score_{barcode}"
        ).delete()[0]
        
        self.logger.info(f"Cleared cache for product {barcode}: {deleted_count} entries")
        return deleted_count
    
    def clear_expired_cache(self) -> int:
        """
        Remove all expired caches.
        
        Returns:
            Number of entries deleted
        """
        deleted_count = ProductCache.clear_expired_cache()
        self.logger.info(f"Cleared expired cache: {deleted_count} entries")
        return deleted_count
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Return cache statistics.
        
        Returns:
            Detailed cache statistics
        """
        stats = ProductCache.get_cache_stats()
        
        # Add statistics by type
        type_stats = {}
        for data_type, _ in ProductCache.DATA_TYPE_CHOICES:
            count = ProductCache.objects.filter(data_type=data_type).count()
            active_count = ProductCache.objects.filter(
                data_type=data_type,
                expires_at__gt=timezone.now()
            ).count()
            
            type_stats[data_type] = {
                'total': count,
                'active': active_count,
                'expired': count - active_count
            }
        
        stats['by_type'] = type_stats
        
        # Top 10 most consulted products
        top_products = ProductCache.objects.filter(
            expires_at__gt=timezone.now()
        ).order_by('-access_count')[:10].values(
            'cache_key', 'data_type', 'access_count', 'last_accessed'
        )
        
        stats['top_products'] = list(top_products)
        
        return stats
    
    def is_cache_available(self) -> bool:
        """
        Check if cache is available.
        
        Returns:
            True if cache is available, False otherwise
        """
        try:
            # Simple test to verify that the model works
            ProductCache.objects.count()
            return True
        except Exception as e:
            self.logger.error(f"Cache not available: {str(e)}")
            return False
