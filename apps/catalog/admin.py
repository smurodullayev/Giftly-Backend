from django.contrib import admin

from .models import Category, Occasion, Product, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


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
        "title", "business", "category", "price", "sale_price",
        "stock", "is_active", "created_at",
    )
    list_filter = ("is_active", "category", "occasions")
    search_fields = ("title", "description", "sku", "business__username")
    list_editable = ("is_active", "stock")
    raw_id_fields = ("business",)
    filter_horizontal = ("occasions", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("slug", "created_at", "updated_at")
    ordering = ("-created_at",)
    fieldsets = (
        ("Asosiy", {"fields": ("business", "title", "slug", "description", "is_active")}),
        ("Narx", {"fields": ("price", "sale_price")}),
        ("Katalog", {"fields": ("category", "occasions", "tags")}),
        ("Inventar", {"fields": ("sku", "stock", "min_order_qty", "weight_grams")}),
        ("Vaqt", {"fields": ("created_at", "updated_at")}),
    )
