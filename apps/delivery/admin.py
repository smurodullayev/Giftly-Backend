from django.contrib import admin

from .models import DeliveryZone


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = (
        "name", "keywords_display", "base_fee", "per_kg_fee",
        "free_above_amount", "is_default", "is_active", "sort_order",
    )
    list_filter = ("is_active", "is_default")
    search_fields = ("name",)
    list_editable = ("is_active", "sort_order", "base_fee", "per_kg_fee")
    ordering = ("sort_order", "name")

    fieldsets = (
        ("Asosiy", {
            "fields": ("name", "keywords", "is_default", "is_active", "sort_order"),
        }),
        ("Narxlar", {
            "fields": ("base_fee", "per_kg_fee", "free_above_amount"),
            "description": "delivery_fee = base_fee + (weight_kg × per_kg_fee)",
        }),
    )

    def keywords_display(self, obj):
        return ", ".join(obj.keywords[:4]) + ("..." if len(obj.keywords) > 4 else "")
    keywords_display.short_description = "Kalit so'zlar"
