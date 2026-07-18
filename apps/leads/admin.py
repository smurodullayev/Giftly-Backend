from django.contrib import admin

from .models import Lead, Order


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "product__title")
    raw_id_fields = ("user", "product")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "lead", "courier", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("lead__user__username", "courier__username")
    raw_id_fields = ("lead", "courier")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
