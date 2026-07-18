from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BusinessProfile, CourierProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "phone", "is_active", "is_staff", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "email", "phone", "first_name", "last_name")
    ordering = ("-date_joined",)
    fieldsets = UserAdmin.fieldsets + (
        ("Giftly", {"fields": ("role", "phone")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Giftly", {"fields": ("role", "phone")}),
    )
    readonly_fields = ("date_joined", "last_login", "updated_at")


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ("company_name", "user", "subscription_plan", "updated_at")
    list_filter = ("subscription_plan",)
    search_fields = ("company_name", "user__username", "user__email")
    raw_id_fields = ("user",)
    readonly_fields = ("updated_at",)


@admin.register(CourierProfile)
class CourierProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "vehicle_type", "is_available", "updated_at")
    list_filter = ("is_available",)
    search_fields = ("user__username",)
    raw_id_fields = ("user",)
    readonly_fields = ("updated_at",)
