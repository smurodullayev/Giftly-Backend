from django.contrib import admin

from .models import Category, Occasion, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "business", "category", "price", "is_active", "created_at")
    list_filter = ("is_active", "category", "occasions")
    search_fields = ("title", "description", "business__username")
    list_editable = ("is_active",)
    raw_id_fields = ("business",)
    filter_horizontal = ("occasions",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
