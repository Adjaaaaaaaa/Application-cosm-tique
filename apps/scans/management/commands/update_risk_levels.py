"""
Commande Django pour mettre à jour les niveaux de risque existants
du système ancien (Low/Medium/High) vers le nouveau système (Excellent/Bon/Médiocre/Mauvais).
"""

from django.core.management.base import BaseCommand
from apps.scans.models import Scan


class Command(BaseCommand):
    help = 'Met à jour les niveaux de risque des scans existants vers le nouveau système de notation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les changements sans les appliquer',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Mapping des anciens vers les nouveaux niveaux
        risk_level_mapping = {
            'Low': 'Excellent',
            'Medium': 'Bon', 
            'High': 'Médiocre',
            # Garder les nouveaux niveaux inchangés
            'Excellent': 'Excellent',
            'Bon': 'Bon',
            'Médiocre': 'Médiocre',
            'Mauvais': 'Mauvais',
        }
        
        # Trouver tous les scans avec des niveaux de risque
        scans_to_update = Scan.objects.exclude(product_risk_level__isnull=True).exclude(product_risk_level='')
        
        updated_count = 0
        unchanged_count = 0
        
        self.stdout.write(f"Traitement de {scans_to_update.count()} scans...")
        
        for scan in scans_to_update:
            old_risk_level = scan.product_risk_level
            new_risk_level = risk_level_mapping.get(old_risk_level, old_risk_level)
            
            if old_risk_level != new_risk_level:
                if dry_run:
                    self.stdout.write(
                        f"Scan {scan.id}: '{old_risk_level}' → '{new_risk_level}' "
                        f"(Produit: {scan.product_name or 'Inconnu'})"
                    )
                else:
                    scan.product_risk_level = new_risk_level
                    scan.save()
                    self.stdout.write(
                        f"✓ Scan {scan.id} mis à jour: '{old_risk_level}' → '{new_risk_level}'"
                    )
                updated_count += 1
            else:
                unchanged_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nMode DRY-RUN: {updated_count} scans seraient mis à jour, "
                    f"{unchanged_count} resteraient inchangés"
                )
            )
            self.stdout.write(
                "Pour appliquer les changements, relancez la commande sans --dry-run"
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Mise à jour terminée: {updated_count} scans mis à jour, "
                    f"{unchanged_count} restés inchangés"
                )
            )
        
        # Afficher un résumé des niveaux actuels
        self.stdout.write("\n📊 Résumé des niveaux de risque actuels:")
        risk_levels = Scan.objects.values_list('product_risk_level', flat=True).distinct()
        for level in risk_levels:
            if level:
                count = Scan.objects.filter(product_risk_level=level).count()
                self.stdout.write(f"  {level}: {count} scans")
