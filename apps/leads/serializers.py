from rest_framework import serializers

from apps.catalog.models import Product
from apps.users.models import User

from .models import Lead, Order


class LeadSerializer(serializers.ModelSerializer):
    """Lead yaratish va o'qish."""

    product_title = serializers.CharField(source="product.title", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id", "user", "user_username",
            "product", "product_title",
            "message", "status",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "user_username", "product_title", "status", "created_at", "updated_at"]

    def validate_product(self, value: Product):
        if not value.is_active:
            raise serializers.ValidationError(
                "Tanlangan mahsulot hozirda mavjud emas."
            )
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class LeadStatusSerializer(serializers.ModelSerializer):
    """Faqat status yangilash uchun (business tomonidan)."""

    class Meta:
        model = Lead
        fields = ["status"]

    def validate_status(self, value):
        allowed = [Lead.Status.CONTACTED, Lead.Status.CLOSED]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Status faqat {[s.value for s in allowed]} qiymatlaridan biri bo'lishi mumkin."
            )
        return value


class OrderSerializer(serializers.ModelSerializer):
    """Buyurtma ko'rish va yaratish."""

    lead_product = serializers.CharField(
        source="lead.product.title", read_only=True
    )
    courier_username = serializers.CharField(
        source="courier.username", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id", "lead", "lead_product",
            "courier", "courier_username",
            "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "lead_product", "courier_username", "created_at", "updated_at"]

    def validate_courier(self, value: User):
        if value is not None and value.role != User.Role.COURIER:
            raise serializers.ValidationError(
                "Tayinlangan foydalanuvchi 'courier' roliga ega bo'lishi kerak."
            )
        return value

    def validate_lead(self, value: Lead):
        # Bir lead uchun faqat bitta order bo'ladi (OneToOne)
        if hasattr(value, "order") and self.instance is None:
            raise serializers.ValidationError(
                "Bu lead uchun buyurtma allaqachon mavjud."
            )
        return value
