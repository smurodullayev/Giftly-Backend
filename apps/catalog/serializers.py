from rest_framework import serializers

from .models import Category, Occasion, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class OccasionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occasion
        fields = ["id", "name"]


class ProductReadSerializer(serializers.ModelSerializer):
    """GET so'rovlari uchun — nested ma'lumotlar bilan."""

    category = CategorySerializer(read_only=True)
    occasions = OccasionSerializer(many=True, read_only=True)
    business_username = serializers.CharField(
        source="business.username", read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id", "business", "business_username",
            "title", "description", "price",
            "category", "occasions",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = fields


class ProductWriteSerializer(serializers.ModelSerializer):
    """POST/PATCH so'rovlari uchun — business auto-set from token."""

    class Meta:
        model = Product
        fields = [
            "title", "description", "price",
            "category", "occasions", "is_active",
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Narx 0 dan katta bo'lishi kerak.")
        return value

    def create(self, validated_data):
        validated_data["business"] = self.context["request"].user
        return super().create(validated_data)
