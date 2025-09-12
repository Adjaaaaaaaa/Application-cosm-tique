"""
Commande Django pour recalculer les niveaux de risque basés sur les nouveaux seuils
(75/50/25 au lieu de 70/40).
"""

from django.core.management.base import BaseCommand
from apps.scans.models import Scan


class Command(BaseCommand):
    help = 'Recalcule les niveaux de risque basés sur les nouveaux seuils (75/50/25)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les changements sans les appliquer',
        )

    def get_risk_level_from_score(self, score):
        """Détermine la notation basée sur le score."""
        if score is None:
            return None
        
        if score >= 75:
            return 'Excellent'
        elif score >= 50:
            return 'Bon'
        elif score >= 25:
            return 'Médiocre'
        else:
            return 'Mauvais'

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Trouver tous les scans avec un score
        scans_with_score = Scan.objects.exclude(product_score__isnull=True)
        
        updated_count = 0
        unchanged_count = 0
        
        self.stdout.write(f"Traitement de {scans_with_score.count()} scans avec score...")
        
        for scan in scans_with_score:
            old_risk_level = scan.product_risk_level
            new_risk_level = self.get_risk_level_from_score(scan.product_score)
            
            if old_risk_level != new_risk_level:
                if dry_run:
                    self.stdout.write(
                        f"Scan {scan.id}: Score {scan.product_score} → '{new_risk_level}' "
                        f"(était '{old_risk_level}') - Produit: {scan.product_name or 'Inconnu'}"
                    )
                else:
                    scan.product_risk_level = new_risk_level
                    scan.save()
                    self.stdout.write(
                        f"✓ Scan {scan.id} mis à jour: Score {scan.product_score} → '{new_risk_level}'"
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
