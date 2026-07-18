from rest_framework import serializers

from apps.catalog.models import Product
from apps.users.models import User

from .models import Lead, Order


class LeadSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    product_price = serializers.DecimalField(
        source="product.effective_price", max_digits=12, decimal_places=2, read_only=True
    )
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id", "user", "user_username",
            "product", "product_title", "product_price",
            "message", "contact_phone", "preferred_delivery_date",
            "status", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "user", "user_username",
            "product_title", "product_price",
            "status", "created_at", "updated_at",
        ]

    def validate_product(self, value: Product):
        if not value.is_active:
            raise serializers.ValidationError("Tanlangan mahsulot hozirda mavjud emas.")
        if not value.is_in_stock:
            raise serializers.ValidationError("Mahsulot omborda qolmagan.")
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class LeadStatusSerializer(serializers.ModelSerializer):
    """Faqat business tomonidan status yangilash uchun."""

    class Meta:
        model = Lead
        fields = ["status"]

    def validate_status(self, value):
        allowed = [Lead.Status.CONTACTED, Lead.Status.CLOSED]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Status faqat {[s.value for s in allowed]} bo'lishi mumkin."
            )
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Buyurtma ko'rish va yaratish."""

    lead_product = serializers.CharField(source="lead.product.title", read_only=True)
    lead_user = serializers.CharField(source="lead.user.username", read_only=True)
    courier_username = serializers.CharField(source="courier.username", read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id", "lead", "lead_product", "lead_user",
            "courier", "courier_username",
            "delivery_address", "notes", "tracking_number",
            "estimated_delivery", "delivered_at",
            "price_snapshot", "delivery_fee", "total_amount",
            "payment_method", "payment_status",
            "status", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "lead_product", "lead_user", "courier_username",
            "total_amount", "created_at", "updated_at",
        ]

    def validate_courier(self, value: User):
        if value is not None and value.role != User.Role.COURIER:
            raise serializers.ValidationError(
                "Tayinlangan foydalanuvchi 'courier' roliga ega bo'lishi kerak."
            )
        return value

    def validate_lead(self, value: Lead):
        if hasattr(value, "order") and self.instance is None:
            raise serializers.ValidationError(
                "Bu lead uchun buyurtma allaqachon mavjud."
            )
        return value

    def validate_price_snapshot(self, value):
        if value <= 0:
            raise serializers.ValidationError("Narx 0 dan katta bo'lishi kerak.")
        return value
