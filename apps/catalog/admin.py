from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Occasion, Product, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("full_path_display", "slug", "parent", "level_display", "icon_preview")
    list_filter = ("parent",)
    search_fields = ("name", "slug")
    readonly_fields = ("slug", "icon_preview_large")
    ordering = ("name",)

    fieldsets = (
        ("Asosiy", {"fields": ("name", "slug", "parent")}),
        ("Ikonka", {"fields": ("icon", "icon_preview_large")}),
    )

    def full_path_display(self, obj):
        return obj.full_path
    full_path_display.short_description = "To'liq yo'l"

    def level_display(self, obj):
        colors = {1: "#2563eb", 2: "#16a34a", 3: "#d97706"}
        level = obj.level
        color = colors.get(level, "#6b7280")
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}-daraja</span>',
            color, level
        )
    level_display.short_description = "Daraja"

    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" style="height:32px; width:32px; object-fit:cover; border-radius:4px;" />',
                obj.icon.url,
            )
        return "—"
    icon_preview.short_description = "Ikonka"

    def icon_preview_large(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" style="height:80px; width:80px; object-fit:cover; border-radius:8px;" />',
                obj.icon.url,
            )
        return "Hali ikonka yuklanmagan"
    icon_preview_large.short_description = "Ko'rinish"


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title", "business", "price", "sale_price",
        "stock", "is_active", "created_at",
    )
    list_filter = ("is_active", "categories", "occasions")
    search_fields = ("title", "description", "sku", "business__username")
    list_editable = ("is_active", "stock")
    raw_id_fields = ("business",)
    filter_horizontal = ("categories", "occasions", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("slug", "created_at", "updated_at")
    ordering = ("-created_at",)
    fieldsets = (
        ("Asosiy", {"fields": ("business", "title", "slug", "description", "is_active")}),
        ("Narx", {"fields": ("price", "sale_price")}),
        ("Katalog", {"fields": ("categories", "occasions", "tags")}),
        ("Inventar", {"fields": ("sku", "stock", "min_order_qty", "weight_grams")}),
        ("Vaqt", {"fields": ("created_at", "updated_at")}),
    )
