"""
Management command pour gérer le cache des analyses de produits.

Usage:
    python manage.py manage_cache --stats          # Afficher les statistiques
    python manage.py manage_cache --clear-expired  # Nettoyer les caches expirés
    python manage.py manage_cache --clear-all      # Vider tout le cache
    python manage.py manage_cache --clear-product 123456789  # Vider le cache d'un produit
"""

from django.core.management.base import BaseCommand, CommandError
from backend.services.product_cache_service import ProductCacheService
from apps.scans.models import ProductCache


class Command(BaseCommand):
    help = 'Gère le cache des analyses de produits pour optimiser les performances'

    def add_arguments(self, parser):
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Afficher les statistiques du cache',
        )
        parser.add_argument(
            '--clear-expired',
            action='store_true',
            help='Supprimer tous les caches expirés',
        )
        parser.add_argument(
            '--clear-all',
            action='store_true',
            help='Vider complètement le cache',
        )
        parser.add_argument(
            '--clear-product',
            type=str,
            help='Supprimer le cache pour un produit spécifique (code-barres)',
        )
        parser.add_argument(
            '--warm-cache',
            action='store_true',
            help='Préchauffer le cache avec des produits populaires',
        )

    def handle(self, *args, **options):
        cache_service = ProductCacheService()
        
        if options['stats']:
            self.show_cache_stats(cache_service)
        
        elif options['clear_expired']:
            self.clear_expired_cache(cache_service)
        
        elif options['clear_all']:
            self.clear_all_cache()
        
        elif options['clear_product']:
            barcode = options['clear_product']
            self.clear_product_cache(cache_service, barcode)
        
        elif options['warm_cache']:
            self.warm_cache(cache_service)
        
        else:
            self.stdout.write(
                self.style.WARNING('Aucune action spécifiée. Utilisez --help pour voir les options.')
            )

    def show_cache_stats(self, cache_service):
        """Affiche les statistiques détaillées du cache."""
        self.stdout.write(self.style.SUCCESS('📊 Statistiques du Cache des Analyses'))
        self.stdout.write('=' * 50)
        
        try:
            stats = cache_service.get_cache_statistics()
            
            # Statistiques générales
            self.stdout.write(f"📦 Total des entrées: {stats['total_entries']}")
            self.stdout.write(f"✅ Entrées actives: {stats['active_entries']}")
            self.stdout.write(f"❌ Entrées expirées: {stats['expired_entries']}")
            self.stdout.write(f"👆 Total des accès: {stats['total_access']}")
            
            if stats['total_entries'] > 0:
                hit_rate = (stats['total_access'] / stats['total_entries']) * 100
                self.stdout.write(f"🎯 Taux d'utilisation moyen: {hit_rate:.1f}%")
            
            self.stdout.write('\n📋 Répartition par type:')
            for data_type, type_stats in stats['by_type'].items():
                if type_stats['total'] > 0:
                    self.stdout.write(
                        f"  • {data_type}: {type_stats['active']} actives, "
                        f"{type_stats['expired']} expirées"
                    )
            
            # Top produits
            if stats['top_products']:
                self.stdout.write('\n🏆 Top 5 des produits les plus consultés:')
                for i, product in enumerate(stats['top_products'][:5], 1):
                    self.stdout.write(
                        f"  {i}. {product['cache_key']} - "
                        f"{product['access_count']} accès"
                    )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de la récupération des statistiques: {str(e)}')
            )

    def clear_expired_cache(self, cache_service):
        """Supprime tous les caches expirés."""
        self.stdout.write('🧹 Nettoyage des caches expirés...')
        
        try:
            deleted_count = cache_service.clear_expired_cache()
            
            if deleted_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {deleted_count} entrées expirées supprimées')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('ℹ️  Aucune entrée expirée trouvée')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors du nettoyage: {str(e)}')
            )

    def clear_all_cache(self):
        """Vide complètement le cache."""
        self.stdout.write('⚠️  ATTENTION: Cette action va supprimer TOUT le cache!')
        
        try:
            total_count = ProductCache.objects.count()
            
            if total_count == 0:
                self.stdout.write(
                    self.style.WARNING('ℹ️  Le cache est déjà vide')
                )
                return
            
            # Demander confirmation
            confirm = input(f'Êtes-vous sûr de vouloir supprimer {total_count} entrées? (oui/non): ')
            
            if confirm.lower() in ['oui', 'o', 'yes', 'y']:
                ProductCache.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {total_count} entrées supprimées')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('❌ Opération annulée')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de la suppression: {str(e)}')
            )

    def clear_product_cache(self, cache_service, barcode):
        """Supprime le cache pour un produit spécifique."""
        self.stdout.write(f'🗑️  Suppression du cache pour le produit {barcode}...')
        
        try:
            deleted_count = cache_service.clear_cache_for_product(barcode)
            
            if deleted_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {deleted_count} entrées supprimées pour {barcode}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'ℹ️  Aucune entrée trouvée pour {barcode}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de la suppression: {str(e)}')
            )

    def warm_cache(self, cache_service):
        """Préchauffe le cache avec des produits populaires."""
        self.stdout.write('🔥 Préchauffage du cache...')
        
        # Liste de produits populaires pour préchauffer le cache
        popular_products = [
            '3017620422003',  # Nutella
            '3017620422004',  # Nutella
            '3017620422005',  # Nutella
            '8711600000000',  # Coca-Cola
            '8711600000001',  # Coca-Cola
            '8711600000002',  # Coca-Cola
        ]
        
        try:
            from apps.scans.services import ProductAnalysisService
            analysis_service = ProductAnalysisService()
            
            warmed_count = 0
            for barcode in popular_products:
                try:
                    # Analyser le produit (ce qui va le mettre en cache)
                    analysis_service.analyze_product(barcode)
                    warmed_count += 1
                    self.stdout.write(f'  ✅ {barcode} mis en cache')
                except Exception as e:
                    self.stdout.write(f'  ❌ Erreur pour {barcode}: {str(e)}')
            
            self.stdout.write(
                self.style.SUCCESS(f'🔥 {warmed_count} produits préchauffés')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors du préchauffage: {str(e)}')
            )
