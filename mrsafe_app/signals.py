from django.db.models.signals import post_save
from django.dispatch import receiver






# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import PremiumProfile  # Adjust if this is placed in a separate signals.py

@receiver(post_save, sender=PremiumProfile)
def sync_premium_status(sender, instance, **kwargs):
    user = instance.user
    if instance.end_date and instance.end_date > now():
        user.is_premium = True
    else:
        user.is_premium = False
    user.save # ✅ Only update this field for optimization
