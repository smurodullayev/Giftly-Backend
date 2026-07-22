from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import BusinessProfile, CourierProfile, User, BusinessLocation, UserLocation


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
                "role", "phone", "birth_date",
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
        "logo_preview", "logotype_preview",
        "company_name", "user", "phone",
        "subscription_plan", "is_verified", "updated_at",
    )
    list_filter = ("subscription_plan", "is_verified")
    search_fields = ("company_name", "user__username", "user__email", "phone")
    raw_id_fields = ("user",)
    readonly_fields = ("logo_preview_large", "logotype_preview_large", "updated_at")
    fieldsets = (
        ("Asosiy", {
            "fields": ("user", "company_name", "description"),
        }),
        ("Brend", {
            "fields": (
                "logo", "logo_preview_large",
                "logotype", "logotype_preview_large",
            ),
            "description": (
                "Logo — kvadrat ikonka (512×512 px, PNG fon yo'q). "
                "Logotip — matnli to'liq logo (1200×400 px)."
            ),
        }),
        ("Aloqa", {
            "fields": ("phone", "website", "instagram_url", "telegram_username"),
        }),
        ("Holat", {
            "fields": ("subscription_plan", "is_verified"),
        }),
        ("Vaqt", {
            "fields": ("updated_at",),
            "classes": ("collapse",),
        }),
    )

    # ------------------------------------------------------------------
    # Preview metodlari
    # ------------------------------------------------------------------

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:36px;width:36px;'
                'object-fit:contain;border-radius:4px;background:#f3f4f6;padding:2px;" />',
                obj.logo.url,
            )
        return "—"
    logo_preview.short_description = "Logo"

    def logotype_preview(self, obj):
        if obj.logotype:
            return format_html(
                '<img src="{}" style="height:36px;max-width:140px;'
                'object-fit:contain;background:#f3f4f6;padding:2px;border-radius:4px;" />',
                obj.logotype.url,
            )
        return "—"
    logotype_preview.short_description = "Logotip"

    def logo_preview_large(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:100px;width:100px;'
                'object-fit:contain;background:#f3f4f6;'
                'padding:8px;border-radius:8px;border:1px solid #e5e7eb;" />',
                obj.logo.url,
            )
        return "Hali yuklanmagan"
    logo_preview_large.short_description = "Logo ko'rinishi"

    def logotype_preview_large(self, obj):
        if obj.logotype:
            return format_html(
                '<img src="{}" style="height:80px;max-width:400px;'
                'object-fit:contain;background:#f3f4f6;'
                'padding:8px;border-radius:8px;border:1px solid #e5e7eb;" />',
                obj.logotype.url,
            )
        return "Hali yuklanmagan"
    logotype_preview_large.short_description = "Logotip ko'rinishi"


@admin.register(CourierProfile)
class CourierProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "vehicle_type", "is_available", "updated_at")
    list_filter = ("is_available",)
    search_fields = ("user__username",)
    raw_id_fields = ("user",)
    readonly_fields = ("updated_at",)


@admin.register(BusinessLocation)
class BusinessLocationAdmin(admin.ModelAdmin):
    list_display = ("business_profile", "location", "name", "created_at")

@admin.register(UserLocation)
class UserLocation(admin.ModelAdmin):
    list_display = ("user", "location", "name", "created_at")
    list_filter = ("user__role",)
    search_fields = ("user__username", "name")
    raw_id_fields = ("user", "location")
    readonly_fields = ("created_at",)
