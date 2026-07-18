from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import BusinessProfile, CourierProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username", "email", "role", "phone",
        "is_verified", "is_active", "is_staff", "date_joined",
    )
    list_filter = ("role", "is_verified", "is_active", "is_staff")
    search_fields = ("username", "email", "phone", "first_name", "last_name", "telegram")
    ordering = ("-date_joined",)
    fieldsets = UserAdmin.fieldsets + (
        ("Giftly", {
            "fields": (
                "role", "phone", "birth_date", "address",
                "telegram", "bio", "is_verified",
            ),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Giftly", {"fields": ("role", "phone")}),
    )
    readonly_fields = ("date_joined", "last_login", "updated_at")


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = (
        "company_name", "user", "phone", "subscription_plan",
        "is_verified", "updated_at",
    )
    list_filter = ("subscription_plan", "is_verified")
    search_fields = ("company_name", "user__username", "user__email", "phone")
    raw_id_fields = ("user",)
    readonly_fields = ("updated_at",)
    fieldsets = (
        ("Asosiy", {"fields": ("user", "company_name", "description")}),
        ("Aloqa", {"fields": ("phone", "address", "website", "instagram_url", "telegram_username")}),
        ("Holat", {"fields": ("subscription_plan", "is_verified")}),
        ("Vaqt", {"fields": ("updated_at",)}),
    )


@admin.register(CourierProfile)
class CourierProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "vehicle_type", "is_available", "updated_at")
    list_filter = ("is_available",)
    search_fields = ("user__username",)
    raw_id_fields = ("user",)
    readonly_fields = ("updated_at",)
