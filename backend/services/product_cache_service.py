"""
Service de cache pour optimiser les performances des analyses de produits.

Ce service gère un cache intelligent qui stocke les résultats d'analyse
pour éviter les appels répétés aux APIs externes.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import timedelta
from django.utils import timezone
from apps.scans.models import ProductCache

logger = logging.getLogger(__name__)


class ProductCacheService:
    """
    Service de cache pour les analyses de produits.
    
    Gère un cache intelligent avec différentes stratégies selon le type de données :
    - Informations produit : 24h
    - Analyses IA : 12h  
    - Scores de sécurité : 48h
    - Analyses complètes : 6h
    """
    
    # Durées de cache par type de données (en heures)
    CACHE_TTL = {
        'product_info': 24,        # Informations produit : 24h
        'ingredient_analysis': 12,  # Analyse ingrédients : 12h
        'barcode_lookup': 24,      # Recherche code-barres : 24h
        'ai_analysis': 12,         # Analyse IA : 12h
        'safety_score': 48,        # Score de sécurité : 48h
        'complete_analysis': 6,    # Analyse complète : 6h
    }
    
    def __init__(self):
        """Initialise le service de cache."""
        self.logger = logger
        self.logger.info("ProductCacheService initialized")
        
        # Cache en mémoire pour les accès ultra-rapides (évite les requêtes SQL)
        self._memory_cache = {}
        self._memory_cache_ttl = {}
    
    def get_cached_analysis(self, barcode: str, user_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Récupère une analyse complète mise en cache.
        
        Args:
            barcode: Code-barres du produit
            user_id: ID de l'utilisateur (optionnel pour cache personnalisé)
            
        Returns:
            Analyse mise en cache ou None si non trouvée/expirée
        """
        # STEP 1: Vérifier le cache en mémoire (ULTRA-RAPIDE)
        memory_key = f"{barcode}_{user_id or 'global'}"
        if memory_key in self._memory_cache:
            if timezone.now() < self._memory_cache_ttl.get(memory_key, timezone.now()):
                self.logger.info(f"⚡ MEMORY CACHE HIT: {barcode}")
                return self._memory_cache[memory_key]
            else:
                # Cache expiré, le supprimer
                del self._memory_cache[memory_key]
                del self._memory_cache_ttl[memory_key]
        
        # STEP 2: Vérifier le cache de base de données (RAPIDE)
        cache_key = self._build_cache_key('complete_analysis', barcode, user_id)
        cached_data = ProductCache.get_cached_data(cache_key, 'complete_analysis')
        
        if cached_data:
            # Mettre en cache en mémoire pour les prochains accès
            self._memory_cache[memory_key] = cached_data
            self._memory_cache_ttl[memory_key] = timezone.now() + timedelta(minutes=30)  # 30 min en mémoire
            self.logger.info(f"💾 DB CACHE HIT: {barcode} (cached in memory)")
            return cached_data
        
        return None
    
    def set_cached_analysis(self, barcode: str, analysis_data: Dict[str, Any], user_id: int = None) -> None:
        """
        Met en cache une analyse complète.
        
        Args:
            barcode: Code-barres du produit
            analysis_data: Données d'analyse à mettre en cache
            user_id: ID de l'utilisateur (optionnel)
        """
        # Mettre en cache en mémoire (ULTRA-RAPIDE)
        memory_key = f"{barcode}_{user_id or 'global'}"
        self._memory_cache[memory_key] = analysis_data
        self._memory_cache_ttl[memory_key] = timezone.now() + timedelta(minutes=30)  # 30 min en mémoire
        
        # Mettre en cache en base de données (PERSISTANT)
        cache_key = self._build_cache_key('complete_analysis', barcode, user_id)
        ttl_hours = self.CACHE_TTL['complete_analysis']
        ProductCache.set_cached_data(cache_key, analysis_data, 'complete_analysis', ttl_hours)
        
        self.logger.info(f"💾 CACHED: {barcode} (Memory: 30min, DB: {ttl_hours}h)")
    
    def get_cached_product_info(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations produit mises en cache.
        
        Args:
            barcode: Code-barres du produit
            
        Returns:
            Informations produit mises en cache ou None
        """
        cache_key = self._build_cache_key('product_info', barcode)
        cached_data = ProductCache.get_cached_data(cache_key, 'product_info')
        
        if cached_data:
            self.logger.info(f"Cache hit for product info: {barcode}")
            return cached_data
        
        return None
    
    def set_cached_product_info(self, barcode: str, product_data: Dict[str, Any]) -> None:
        """
        Met en cache les informations produit.
        
        Args:
            barcode: Code-barres du produit
            product_data: Données produit à mettre en cache
        """
        cache_key = self._build_cache_key('product_info', barcode)
        ttl_hours = self.CACHE_TTL['product_info']
        
        ProductCache.set_cached_data(cache_key, product_data, 'product_info', ttl_hours)
        self.logger.info(f"Cached product info: {barcode} (TTL: {ttl_hours}h)")
    
    def get_cached_ai_analysis(self, barcode: str, user_id: int, question: str = None) -> Optional[Dict[str, Any]]:
        """
        Récupère une analyse IA mise en cache.
        
        Args:
            barcode: Code-barres du produit
            user_id: ID de l'utilisateur
            question: Question spécifique (optionnel)
            
        Returns:
            Analyse IA mise en cache ou None
        """
        cache_key = self._build_cache_key('ai_analysis', barcode, user_id, question)
        cached_data = ProductCache.get_cached_data(cache_key, 'ai_analysis')
        
        if cached_data:
            self.logger.info(f"Cache hit for AI analysis: {barcode} (user: {user_id})")
            return cached_data
        
        return None
    
    def set_cached_ai_analysis(self, barcode: str, user_id: int, analysis_data: Dict[str, Any], question: str = None) -> None:
        """
        Met en cache une analyse IA.
        
        Args:
            barcode: Code-barres du produit
            user_id: ID de l'utilisateur
            analysis_data: Données d'analyse IA à mettre en cache
            question: Question spécifique (optionnel)
        """
        cache_key = self._build_cache_key('ai_analysis', barcode, user_id, question)
        ttl_hours = self.CACHE_TTL['ai_analysis']
        
        ProductCache.set_cached_data(cache_key, analysis_data, 'ai_analysis', ttl_hours)
        self.logger.info(f"Cached AI analysis: {barcode} (user: {user_id}, TTL: {ttl_hours}h)")
    
    def get_cached_safety_score(self, barcode: str, user_id: int = None) -> Optional[Dict[str, Any]]:
        """
        Récupère un score de sécurité mis en cache.
        
        Args:
            barcode: Code-barres du produit
            user_id: ID de l'utilisateur (optionnel)
            
        Returns:
            Score de sécurité mis en cache ou None
        """
        cache_key = self._build_cache_key('safety_score', barcode, user_id)
        cached_data = ProductCache.get_cached_data(cache_key, 'safety_score')
        
        if cached_data:
            self.logger.info(f"Cache hit for safety score: {barcode}")
            return cached_data
        
        return None
    
    def set_cached_safety_score(self, barcode: str, safety_data: Dict[str, Any], user_id: int = None) -> None:
        """
        Met en cache un score de sécurité.
        
        Args:
            barcode: Code-barres du produit
            safety_data: Données de sécurité à mettre en cache
            user_id: ID de l'utilisateur (optionnel)
        """
        cache_key = self._build_cache_key('safety_score', barcode, user_id)
        ttl_hours = self.CACHE_TTL['safety_score']
        
        ProductCache.set_cached_data(cache_key, safety_data, 'safety_score', ttl_hours)
        self.logger.info(f"Cached safety score: {barcode} (TTL: {ttl_hours}h)")
    
    def _build_cache_key(self, data_type: str, barcode: str, user_id: int = None, question: str = None) -> str:
        """
        Construit une clé de cache unique.
        
        Args:
            data_type: Type de données
            barcode: Code-barres du produit
            user_id: ID de l'utilisateur (optionnel)
            question: Question spécifique (optionnel)
            
        Returns:
            Clé de cache unique
        """
        key_parts = [data_type, barcode]
        
        if user_id:
            key_parts.append(f"user_{user_id}")
        
        if question:
            # Créer un hash de la question pour éviter des clés trop longues
            import hashlib
            question_hash = hashlib.md5(question.encode()).hexdigest()[:8]
            key_parts.append(f"q_{question_hash}")
        
        return "_".join(key_parts)
    
    def clear_cache_for_product(self, barcode: str) -> int:
        """
        Supprime tous les caches pour un produit spécifique.
        
        Args:
            barcode: Code-barres du produit
            
        Returns:
            Nombre d'entrées supprimées
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
        Supprime tous les caches expirés.
        
        Returns:
            Nombre d'entrées supprimées
        """
        deleted_count = ProductCache.clear_expired_cache()
        self.logger.info(f"Cleared expired cache: {deleted_count} entries")
        return deleted_count
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du cache.
        
        Returns:
            Statistiques détaillées du cache
        """
        stats = ProductCache.get_cache_stats()
        
        # Ajouter des statistiques par type
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
        
        # Top 10 des produits les plus consultés
        top_products = ProductCache.objects.filter(
            expires_at__gt=timezone.now()
        ).order_by('-access_count')[:10].values(
            'cache_key', 'data_type', 'access_count', 'last_accessed'
        )
        
        stats['top_products'] = list(top_products)
        
        return stats
    
    def is_cache_available(self) -> bool:
        """
        Vérifie si le cache est disponible.
        
        Returns:
            True si le cache est disponible, False sinon
        """
        try:
            # Test simple pour vérifier que le modèle fonctionne
            ProductCache.objects.count()
            return True
        except Exception as e:
            self.logger.error(f"Cache not available: {str(e)}")
            return False
