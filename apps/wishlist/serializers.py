from rest_framework import serializers

from apps.catalog.models import Product
from .models import WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    """Wishlist elementi — mahsulot ma'lumotlari bilan."""

    product_title = serializers.CharField(source="product.title", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)
    product_price = serializers.DecimalField(
        source="product.effective_price", max_digits=12, decimal_places=2, read_only=True
    )
    product_is_active = serializers.BooleanField(source="product.is_active", read_only=True)

    class Meta:
        model = WishlistItem
        fields = [
            "id", "product",
            "product_title", "product_slug",
            "product_price", "product_is_active",
            "created_at",
        ]
        read_only_fields = [
            "id", "product_title", "product_slug",
            "product_price", "product_is_active", "created_at",
        ]

    def validate_product(self, product):
        user = self.context["request"].user
        if WishlistItem.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError(
                "Bu mahsulot allaqachon wishlistingizda mavjud."
            )
        return product

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
