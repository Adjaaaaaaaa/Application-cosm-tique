"""
Tests de performance pour le système de cache des analyses de produits.

Ces tests vérifient que le cache améliore significativement les performances
des analyses de produits.
"""

import time
import unittest
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.scans.services import ProductAnalysisService
from backend.services.product_cache_service import ProductCacheService
from apps.scans.models import ProductCache


class CachePerformanceTests(TestCase):
    """Tests de performance du système de cache."""
    
    def setUp(self):
        """Configuration des tests."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.analysis_service = ProductAnalysisService()
        self.cache_service = ProductCacheService()
        
        # Code-barres de test
        self.test_barcode = "1234567890123"
    
    def tearDown(self):
        """Nettoyage après les tests."""
        # Supprimer le cache de test
        ProductCache.objects.filter(cache_key__contains=self.test_barcode).delete()
    
    def test_cache_miss_then_hit_performance(self):
        """
        Test que le cache améliore les performances.
        
        Premier appel : cache miss (lent)
        Deuxième appel : cache hit (rapide)
        """
        # Premier appel - cache miss
        start_time = time.time()
        result1 = self.analysis_service.analyze_product(self.test_barcode, self.user.id)
        first_call_time = time.time() - start_time
        
        # Vérifier que le résultat est mis en cache
        cached_result = self.cache_service.get_cached_analysis(self.test_barcode, self.user.id)
        self.assertIsNotNone(cached_result, "Le résultat devrait être mis en cache")
        
        # Deuxième appel - cache hit
        start_time = time.time()
        result2 = self.analysis_service.analyze_product(self.test_barcode, self.user.id)
        second_call_time = time.time() - start_time
        
        # Vérifier que les résultats sont identiques
        self.assertEqual(result1['product'].get('name', ''), result2['product'].get('name', ''))
        
        # Vérifier que le deuxième appel est plus rapide
        self.assertLess(
            second_call_time, 
            first_call_time,
            f"Le cache devrait être plus rapide. Premier appel: {first_call_time:.3f}s, "
            f"Deuxième appel: {second_call_time:.3f}s"
        )
        
        # Le deuxième appel devrait être au moins 10x plus rapide
        speed_improvement = first_call_time / second_call_time
        self.assertGreater(
            speed_improvement, 
            10,
            f"Le cache devrait être au moins 10x plus rapide. "
            f"Amélioration: {speed_improvement:.1f}x"
        )
        
        print(f"✅ Performance test passed:")
        print(f"   Premier appel (cache miss): {first_call_time:.3f}s")
        print(f"   Deuxième appel (cache hit): {second_call_time:.3f}s")
        print(f"   Amélioration: {speed_improvement:.1f}x plus rapide")
    
    def test_cache_expiration(self):
        """Test que le cache expire correctement."""
        # Mettre en cache un résultat
        test_data = {"test": "data", "barcode": self.test_barcode}
        self.cache_service.set_cached_analysis(self.test_barcode, test_data, self.user.id)
        
        # Vérifier que le cache est disponible
        cached_result = self.cache_service.get_cached_analysis(self.test_barcode, self.user.id)
        self.assertIsNotNone(cached_result, "Le cache devrait être disponible")
        
        # Simuler l'expiration en modifiant directement la base de données
        cache_entry = ProductCache.objects.get(cache_key__contains=self.test_barcode)
        cache_entry.expires_at = timezone.now() - timedelta(hours=1)
        cache_entry.save()
        
        # Vérifier que le cache expiré n'est plus disponible
        expired_result = self.cache_service.get_cached_analysis(self.test_barcode, self.user.id)
        self.assertIsNone(expired_result, "Le cache expiré ne devrait plus être disponible")
    
    def test_cache_statistics(self):
        """Test des statistiques du cache."""
        # Mettre en cache quelques données
        test_data = {"test": "data"}
        self.cache_service.set_cached_analysis(self.test_barcode, test_data, self.user.id)
        
        # Récupérer les statistiques
        stats = self.cache_service.get_cache_statistics()
        
        # Vérifier que les statistiques sont correctes
        self.assertIn('total_entries', stats)
        self.assertIn('active_entries', stats)
        self.assertIn('expired_entries', stats)
        self.assertIn('total_access', stats)
        self.assertIn('by_type', stats)
        
        # Vérifier qu'il y a au moins une entrée
        self.assertGreaterEqual(stats['total_entries'], 1)
        self.assertGreaterEqual(stats['active_entries'], 1)
    
    def test_cache_clear_functionality(self):
        """Test de la fonctionnalité de nettoyage du cache."""
        # Mettre en cache un résultat
        test_data = {"test": "data"}
        self.cache_service.set_cached_analysis(self.test_barcode, test_data, self.user.id)
        
        # Vérifier que le cache est disponible
        cached_result = self.cache_service.get_cached_analysis(self.test_barcode, self.user.id)
        self.assertIsNotNone(cached_result, "Le cache devrait être disponible")
        
        # Supprimer le cache pour ce produit
        deleted_count = self.cache_service.clear_cache_for_product(self.test_barcode)
        self.assertGreater(deleted_count, 0, "Au moins une entrée devrait être supprimée")
        
        # Vérifier que le cache n'est plus disponible
        cleared_result = self.cache_service.get_cached_analysis(self.test_barcode, self.user.id)
        self.assertIsNone(cleared_result, "Le cache devrait être supprimé")
    
    def test_cache_key_generation(self):
        """Test de la génération des clés de cache."""
        # Tester différentes combinaisons de paramètres
        key1 = self.cache_service._build_cache_key('test_type', '123', None, None)
        key2 = self.cache_service._build_cache_key('test_type', '123', 1, None)
        key3 = self.cache_service._build_cache_key('test_type', '123', 1, 'question')
        
        # Vérifier que les clés sont différentes
        self.assertNotEqual(key1, key2, "Les clés avec user_id différent devraient être différentes")
        self.assertNotEqual(key2, key3, "Les clés avec question différente devraient être différentes")
        
        # Vérifier le format des clés
        self.assertTrue(key1.startswith('test_type_123'))
        self.assertTrue(key2.startswith('test_type_123_user_1'))
        self.assertTrue(key3.startswith('test_type_123_user_1_q_'))


if __name__ == '__main__':
    unittest.main()
