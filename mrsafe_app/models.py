from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from datetime import timedelta

# ==============================
# ✅ Custom User Model
# ==============================
class CustomUser(AbstractUser, PermissionsMixin):
    is_premium = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    coins = models.PositiveIntegerField(default=0)
    trainees = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="trainers")

    def has_premium_access(self):
        return self.is_premium or self.coins >= 100


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
class PremiumPlan(models.Model):
    PLAN_CHOICES = [
        ('trial', 'Trial'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    duration_days = models.PositiveIntegerField()
    coin_bonus = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_name_display()} Plan - {self.duration_days} days"


class PremiumProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    auto_renewal = models.BooleanField(default=True)
    plan = models.ForeignKey(PremiumPlan, null=True, blank=True, on_delete=models.SET_NULL)
    trial_used = models.BooleanField(default=False)
    premium_code = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    premium_start_date = models.DateTimeField(null=True, blank=True)
    premium_end_date = models.DateTimeField(null=True, blank=True)
    coin_balance = models.PositiveIntegerField(default=0)


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
class UserCoinBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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

        # Record transaction
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


from django.db import models
from django.conf import settings

class SiteInspection(models.Model):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} @ {self.location} ({self.date.strftime('%Y-%m-%d')})"

    def total_observations(self):
        return self.observations.count()

class SafetyObservation(models.Model):
    photo = models.ImageField(upload_to='observations/')
    hazard_description = models.TextField()
    recommendations = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    site_inspection = models.ForeignKey(
        SiteInspection,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="observations"
    )

    def __str__(self):
        return f"Observation {self.id} - {self.detected_at.strftime('%Y-%m-%d %H:%M')}"
