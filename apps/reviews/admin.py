from django.contrib import admin
from django.utils.html import format_html

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "user", "product", "rating_stars", "is_verified_purchase",
        "has_reply", "created_at",
    )
    list_filter = ("rating", "is_verified_purchase")
    search_fields = ("user__username", "product__title", "comment")
    readonly_fields = ("is_verified_purchase", "replied_at", "created_at", "updated_at")
    ordering = ("-created_at",)
    raw_id_fields = ("user", "product")

    fieldsets = (
        ("Sharh", {
            "fields": ("user", "product", "rating", "comment", "is_verified_purchase"),
        }),
        ("Biznes javobi", {
            "fields": ("reply", "replied_at"),
        }),
        ("Vaqt", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def rating_stars(self, obj):
        stars = "★" * obj.rating + "☆" * (5 - obj.rating)
        colors = {5: "#16a34a", 4: "#65a30d", 3: "#d97706", 2: "#ea580c", 1: "#dc2626"}
        return format_html(
            '<span style="color:{}; font-size:1.1em;">{}</span>',
            colors.get(obj.rating, "#6b7280"),
            stars,
        )
    rating_stars.short_description = "Reyting"

    def has_reply(self, obj):
        if obj.reply:
            return format_html('<span style="color:#16a34a;">✓ Javob bor</span>')
        return format_html('<span style="color:#9ca3af;">—</span>')
    has_reply.short_description = "Javob"
