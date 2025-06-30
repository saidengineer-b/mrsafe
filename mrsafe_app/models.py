from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from datetime import timedelta

# ==============================
# ✅ Custom User Model
# ==============================
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.functional import cached_property

class CustomUser(AbstractUser, PermissionsMixin):
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    coins = models.PositiveIntegerField(default=0)
    trainees = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="trainers")

    @cached_property
    def has_premium_access(self):
        """Check premium access through PremiumProfile or coin balance"""
        return (hasattr(self, 'premium_profile') and 
               (self.premium_profile.is_premium_active() or self.coins >= 100))

    @cached_property
    def is_premium(self):
        """Legacy-compatible property (if absolutely needed)"""
        return self.has_premium_access

    @cached_property
    def premium_expiry_date(self):
        """Get premium expiry date if available"""
        if hasattr(self, 'premium_profile'):
            return self.premium_profile.end_date
        return None

    def get_premium_status(self):
        """Explicit method for when properties aren't suitable"""
        return {
            'has_access': self.has_premium_access,
            'expiry_date': self.premium_expiry_date,
            'is_trial': getattr(self.premium_profile, 'trial_used', False)
        }

# ==============================
# ✅ Store Models
# ==============================
class StoreItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    item_type = models.CharField(max_length=20)
    coins_amount = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='store_items/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.item.name}"


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(StoreItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.item.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.item.name}"


# ==============================
# ✅ Premium Membership
# ==============================

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify

class PremiumPlan(models.Model):
    class PlanType(models.TextChoices):
        TRIAL = 'trial', _('Trial')
        WEEKLY = 'weekly', _('Weekly')
        MONTHLY = 'monthly', _('Monthly')
        ANNUAL = 'annual', _('Annual')
    slug = models.SlugField(
    unique=True,
    blank=True,
    null=True,
    verbose_name=_("Slug")
)

    name = models.CharField(
        max_length=50,
        choices=PlanType.choices,
        unique=True,
        verbose_name=_("Plan Type")
    )
    duration_days = models.PositiveIntegerField(
        verbose_name=_("Duration in Days"),
        validators=[MinValueValidator(1)]
    )
    coin_bonus = models.PositiveIntegerField(
        verbose_name=_("Coin Bonus"),
        default=0
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name=_("Price"),
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active Status")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Plan Description")
    )
    features = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Plan Features"),
        help_text=_("List of features for this plan")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,  # This will auto-set on creation
        verbose_name=_("Created At")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )

    class Meta:
        verbose_name = _("Premium Plan")
        verbose_name_plural = _("Premium Plans")
        ordering = ['duration_days']

    def __str__(self):
        return f"{self.get_name_display()} Plan - {self.duration_days} days"

    def is_trial(self):
        return self.name == self.PlanType.TRIAL

    def get_duration_months(self):
        """Convert duration in days to approximate months"""
        return round(self.duration_days / 30, 1)


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while PremiumPlan.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import transaction

class PremiumProfile(models.Model):
    """
    Enhanced premium membership profile with robust features
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='premium_profile',
        verbose_name="User Account"
    )
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Membership Start"
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Membership End"
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Active Status"
    )
    auto_renewal = models.BooleanField(
        default=True,
        verbose_name="Auto-Renewal"
    )
    plan = models.ForeignKey(
        'PremiumPlan',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Subscription Plan"
    )
    trial_used = models.BooleanField(
        default=False,
        verbose_name="Trial Period Used"
    )
    premium_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Activation Code"
    )
    last_payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Payment"
    )
    payment_method = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Payment Method"
    )

    class Meta:
        verbose_name = "Premium Membership"
        verbose_name_plural = "Premium Memberships"
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['is_active', 'end_date']),
            models.Index(fields=['user', 'trial_used']),
        ]

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.user.username}'s Premium ({status})"

    def clean(self):
        """Validation rules"""
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date")
        if self.trial_used and self.plan and self.plan.name == 'trial':
            raise ValidationError("Trial plan cannot be reused")

    def save(self, *args, **kwargs):
        """Auto-update active status based on dates"""
        self.full_clean()  # Enforce validation
        if self.end_date and self.end_date > timezone.now():
            self.is_active = True
        super().save(*args, **kwargs)

    @transaction.atomic
    def activate_premium(self, plan_name="trial", duration_days=3, coin_bonus=50):
        """
        Safely activates premium membership with transaction support
        """
        from .models import PremiumPlan  # Avoid circular imports
        
        try:
            plan = PremiumPlan.objects.get(name=plan_name)
        except PremiumPlan.DoesNotExist:
            plan = None

        now = timezone.now()
        self.start_date = now
        self.end_date = now + timedelta(days=duration_days)
        self.is_active = True
        self.plan = plan
        
        if plan_name == 'trial':
            self.trial_used = True
            
        self.save()
        
        # Update user's coins atomically
        if coin_bonus > 0:
            self.user.coins = models.F('coins') + coin_bonus
            self.user.save(update_fields=['coins'])

    def deactivate_premium(self):
        """Immediately cancels premium membership"""
        self.is_active = False
        self.auto_renewal = False
        self.save()

    def is_premium_active(self):
        """Check current premium status with auto-expiration"""
        if not self.is_active:
            return False
        if self.end_date and timezone.now() > self.end_date:
            self.is_active = False
            self.save()
            return False
        return True

    def days_remaining(self):
        """Calculates remaining premium days"""
        if not self.is_active or not self.end_date:
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)  # Never return negative

    def renew(self, duration_days):
        """Extends premium membership"""
        if not self.end_date or timezone.now() > self.end_date:
            self.end_date = timezone.now()
        self.end_date += timedelta(days=duration_days)
        self.is_active = True
        self.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_premium_profile(sender, instance, created, **kwargs):
    """
    Ensures every user has a premium profile
    Handles case where profile might exist without signal
    """
    if created or not hasattr(instance, 'premium_profile'):
        PremiumProfile.objects.get_or_create(user=instance)
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="User"
    )
    coin_balance = models.PositiveIntegerField(
        default=0,
        verbose_name="Coin Balance"
    )
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    @property
    def is_premium(self):
        """Check premium status through PremiumProfile"""
        return hasattr(self.user, 'premium_profile') and \
               self.user.premium_profile.is_premium_active()

    @property
    def premium_expiry_date(self):
        """Get premium expiry date if available"""
        if hasattr(self.user, 'premium_profile'):
            return self.user.premium_profile.end_date
        return None

    def add_coins(self, amount):
        """Safely add coins to balance"""
        self.coin_balance = models.F('coin_balance') + amount
        self.save(update_fields=['coin_balance'])

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='profile')
    coin_balance = models.PositiveIntegerField(default=0)
    
    # Removed premium-related fields since they're now in PremiumProfile
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    @property
    def is_premium(self):
        """Check premium status through PremiumProfile"""
        if hasattr(self.user, 'premium_profile'):
            return self.user.premium_profile.is_premium_active()
        return False

    @property
    def premium_expiry_date(self):
        """Get premium expiry date if available"""
        if hasattr(self.user, 'premium_profile'):
            return self.user.premium_profile.end_date
        return None


# ==============================
# ✅ Legal Documents
# ==============================
class TermsAndConditions(models.Model):
    title = models.CharField(max_length=255, default="Terms and Conditions")
    content = models.TextField()

    def __str__(self):
        return self.title


class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=255, default="Privacy Policy")
    content = models.TextField()

    def __str__(self):
        return self.title


# ==============================
# ✅ Notifications
# ==============================
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('system', 'System'),
        ('payment', 'Payment'),
        ('warning', 'Warning'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


# ==============================
# ✅ Coins System
# ==============================
from django.db import models, transaction
from django.conf import settings

# ==============================
# ✅ CoinActivity: Defines each earning/spending activity
# ==============================
class CoinActivity(models.Model):
    ACTIVITY_TYPES = [
        ('earn', 'Earn Coins'),
        ('spend', 'Spend Coins'),
    ]

    name = models.CharField(max_length=255, unique=True)
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPES, default='earn')
    coin_amount = models.PositiveIntegerField(null=True, blank=True)
    default_description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_activity_type_display()} - {self.coin_amount or '?'} Coins)"


# ==============================
# ✅ CoinTransaction: Stores history of all coin activity
# ==============================
class CoinTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('earned', 'Earned'),
        ('spent', 'Spent'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity = models.ForeignKey(CoinActivity, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    reference_id = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        activity_name = self.activity.name if self.activity else 'Unknown'
        return f"{self.user.username} {self.transaction_type} {self.amount} coins for {activity_name}"


# ==============================
# ✅ UserCoinBalance: One-to-One balance per user
# ==============================
from django.db import models, transaction
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserCoinBalance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coin_balance_obj"
    )
    balance = models.PositiveIntegerField(default=0)

    @transaction.atomic
    def update_balance(self, amount, action, activity=None):
        if amount <= 0:
            return False

        if action == "earn":
            self.balance += amount
            transaction_type = "earned"
        elif action == "spend":
            if self.balance < amount:
                return False
            self.balance -= amount
            transaction_type = "spent"
        else:
            return False

        self.save()

        # Record transaction if activity given
        if activity:
            CoinTransaction.objects.create(
                user=self.user,
                amount=amount,
                transaction_type=transaction_type,
                activity=activity
            )

        return True

    def add_coins(self, amount):
        return self.update_balance(amount, action="earn")

    def deduct_coins(self, amount):
        return self.update_balance(amount, action="spend")

    def __str__(self):
        return f"{self.user.username} – {self.balance} coins"

# ✅ Automatically create coin balance for new users
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_coin_balance(sender, instance, created, **kwargs):
    if created:
        UserCoinBalance.objects.get_or_create(user=instance)


# ==============================
# ✅ Ads / Monetization
# ==============================
class AdActivity(models.Model):
    CONTEXT_CHOICES = [
        ('inspection_done', 'Inspection Completed'),
        ('report_generated', 'Report Generated'),
    ]

    name = models.CharField(max_length=100, choices=CONTEXT_CHOICES, unique=True)
    ad_type = models.CharField(max_length=20, choices=[
        ('display', 'Display Ad'),
        ('video', 'Video Ad'),
        ('rewarded', 'Rewarded Ad'),
    ])
    ad_value = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.get_name_display()} - {self.get_ad_type_display()}"


# ==============================
# ✅ Categories / Payments
# ==============================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PaymentTransaction(models.Model):
    PAYMENT_METHODS = [
        ('google_pay', 'Google Pay'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('manual', 'Manual Entry'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    gateway_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} paid {self.amount} {self.currency} via {self.get_payment_method_display()}"

from django.utils import timezone

class SiteInspection(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # ✅ Add these fields
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} @ {self.location} ({self.date.strftime('%Y-%m-%d')})"

    def total_observations(self):
        return self.observations.count()

from django.db import models
from django.conf import settings

class SafetyObservation(models.Model):
    photo = models.ImageField(upload_to='observations/')
    hazard_description = models.TextField()
    recommendations = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="safety_observations"
    )

    site_inspection = models.ForeignKey(
        'SiteInspection',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="observations"
    )

    structured_json = models.JSONField(null=True, blank=True)  # ✅ ADD THIS FIELD

    def __str__(self):
        return f"Observation {self.id} - {self.detected_at.strftime('%Y-%m-%d %H:%M')}"
