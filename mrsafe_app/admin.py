

# Check if this line is duplicated:
from django.contrib import admin
from .models import StoreItem

from django.contrib import admin
from .models import TermsAndConditions, PrivacyPolicy

admin.site.register(TermsAndConditions)
admin.site.register(PrivacyPolicy)





from django.contrib import admin




from django.contrib import admin
from .models import AdActivity

@admin.register(AdActivity)
class AdActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'ad_type', 'ad_value', 'is_active', 'start_date', 'end_date')
    list_filter = ('ad_type', 'is_active')
    search_fields = ('name',)

# mrsafe_app/admin.py
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("message", "user__username")
