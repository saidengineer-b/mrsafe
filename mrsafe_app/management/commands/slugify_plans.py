from django.core.management.base import BaseCommand
from mrsafe_app.models import PremiumPlan
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Auto-generate slug for all PremiumPlan entries"

    def handle(self, *args, **kwargs):
        updated = 0
        for plan in PremiumPlan.objects.all():
            if not plan.slug:
                plan.slug = slugify(plan.name)
                plan.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Updated {updated} PremiumPlan slugs."))
