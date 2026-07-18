from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Coupon, CouponUsage


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ("user", "order_amount", "discount_applied", "used_at")
    can_delete = False


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code", "discount_type", "discount_value_display",
        "used_count", "max_uses", "status_badge",
        "valid_until", "is_active",
    )
    list_filter = ("discount_type", "is_active", "one_per_user")
    search_fields = ("code", "description")
    list_editable = ("is_active",)
    ordering = ("-created_at",)
    readonly_fields = ("used_count", "created_at")
    inlines = [CouponUsageInline]

    fieldsets = (
        ("Asosiy", {
            "fields": ("code", "description", "is_active"),
        }),
        ("Chegirma", {
            "fields": ("discount_type", "discount_value", "max_discount_amount", "min_order_amount"),
        }),
        ("Cheklovlar", {
            "fields": ("max_uses", "used_count", "one_per_user"),
        }),
        ("Muddat", {
            "fields": ("valid_from", "valid_until"),
        }),
        ("Ma'lumot", {
            "fields": ("created_at",),
            "classes": ("collapse",),
        }),
    )

    def discount_value_display(self, obj):
        if obj.discount_type == Coupon.DiscountType.PERCENT:
            return f"{obj.discount_value}%"
        return f"{obj.discount_value:,.0f} so'm"
    discount_value_display.short_description = "Chegirma"

    def status_badge(self, obj):
        now = timezone.now()
        if not obj.is_active:
            return format_html('<span style="color:#6b7280;">Nofaol</span>')
        if obj.valid_until and now > obj.valid_until:
            return format_html('<span style="color:#dc2626;">Muddati tugagan</span>')
        if obj.max_uses and obj.used_count >= obj.max_uses:
            return format_html('<span style="color:#d97706;">Limit tugagan</span>')
        return format_html('<span style="color:#16a34a;">✓ Faol</span>')
    status_badge.short_description = "Holat"


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ("coupon", "user", "order_amount", "discount_applied", "used_at")
    search_fields = ("coupon__code", "user__username")
    raw_id_fields = ("user", "coupon")
    ordering = ("-used_at",)
    readonly_fields = ("used_at",)
