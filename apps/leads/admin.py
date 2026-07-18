from django.contrib import admin

from .models import Lead, Order


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "status", "contact_phone", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "product__title", "contact_phone")
    raw_id_fields = ("user", "product")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "lead", "courier", "status", "payment_status",
        "price_snapshot", "delivery_fee", "total_amount", "created_at",
    )
    list_filter = ("status", "payment_status", "payment_method")
    search_fields = (
        "lead__user__username", "courier__username",
        "tracking_number", "delivery_address",
    )
    raw_id_fields = ("lead", "courier")
    readonly_fields = ("total_amount", "created_at", "updated_at")
    ordering = ("-created_at",)
    fieldsets = (
        ("Asosiy", {"fields": ("lead", "status")}),
        ("Yetkazish", {"fields": (
            "courier", "delivery_address", "notes",
            "tracking_number", "estimated_delivery", "delivered_at",
        )}),
        ("Narx", {"fields": ("price_snapshot", "delivery_fee", "total_amount")}),
        ("To'lov", {"fields": ("payment_method", "payment_status")}),
        ("Vaqt", {"fields": ("created_at", "updated_at")}),
    )
