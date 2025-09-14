"""
Django command to recalculate risk levels based on new thresholds
(75/50/25 instead of 70/40).
"""

from django.core.management.base import BaseCommand
from apps.scans.models import Scan


class Command(BaseCommand):
    help = 'Recalculates risk levels based on new thresholds (75/50/25)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show changes without applying them',
        )

    def get_risk_level_from_score(self, score):
        """Determine rating based on score."""
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
        
        # Find all scans with a score
        scans_with_score = Scan.objects.exclude(product_score__isnull=True)
        
        updated_count = 0
        unchanged_count = 0
        
        self.stdout.write(f"Processing {scans_with_score.count()} scans with score...")
        
        for scan in scans_with_score:
            old_risk_level = scan.product_risk_level
            new_risk_level = self.get_risk_level_from_score(scan.product_score)
            
            if old_risk_level != new_risk_level:
                if dry_run:
                    self.stdout.write(
                        f"Scan {scan.id}: Score {scan.product_score} → '{new_risk_level}' "
                        f"(was '{old_risk_level}') - Product: {scan.product_name or 'Unknown'}"
                    )
                else:
                    scan.product_risk_level = new_risk_level
                    scan.save()
                    self.stdout.write(
                        f"✓ Scan {scan.id} updated: Score {scan.product_score} → '{new_risk_level}'"
                    )
                updated_count += 1
            else:
                unchanged_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nDRY-RUN mode: {updated_count} scans would be updated, "
                    f"{unchanged_count} would remain unchanged"
                )
            )
            self.stdout.write(
                "To apply changes, run the command again without --dry-run"
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Update completed: {updated_count} scans updated, "
                    f"{unchanged_count} remained unchanged"
                )
            )
        
        # Display summary of current levels
        self.stdout.write("\n📊 Summary of current risk levels:")
        risk_levels = Scan.objects.values_list('product_risk_level', flat=True).distinct()
        for level in risk_levels:
            if level:
                count = Scan.objects.filter(product_risk_level=level).count()
                self.stdout.write(f"  {level}: {count} scans")
