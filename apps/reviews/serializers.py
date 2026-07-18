from rest_framework import serializers

from apps.leads.models import Order
from .models import Review


class ReviewReadSerializer(serializers.ModelSerializer):
    """Sharhni ko'rish uchun — nested foydalanuvchi ma'lumoti bilan."""

    user_username = serializers.CharField(source="user.username", read_only=True)
    user_full_name = serializers.SerializerMethodField()
    product_title = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "product", "product_title",
            "user", "user_username", "user_full_name",
            "rating", "comment",
            "is_verified_purchase",
            "reply", "replied_at",
            "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_user_full_name(self, obj) -> str:
        return obj.user.get_full_name() or obj.user.username


class ReviewWriteSerializer(serializers.ModelSerializer):
    """Sharh yaratish va tahrirlash uchun."""

    class Meta:
        model = Review
        fields = ["product", "rating", "comment"]

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Reyting 1 dan 5 gacha bo'lishi kerak.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs.get("product") or (self.instance.product if self.instance else None)

        # Buyurtma tekshiruvi — faqat create da (update da o'zgarmaydi)
        if not self.instance:
            has_delivered_order = Order.objects.filter(
                lead__user=user,
                lead__product=product,
                status=Order.Status.DELIVERED,
            ).exists()
            if not has_delivered_order:
                raise serializers.ValidationError(
                    "Sharh yozish uchun mahsulotni sotib olib, "
                    "yetkazib olgan bo'lishingiz kerak."
                )

            # Takroriy sharh tekshiruvi
            if Review.objects.filter(user=user, product=product).exists():
                raise serializers.ValidationError(
                    "Siz bu mahsulotga allaqachon sharh yozgansiz."
                )

        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Sharhni tahrirlash — faqat rating va comment."""

    class Meta:
        model = Review
        fields = ["rating", "comment"]

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Reyting 1 dan 5 gacha bo'lishi kerak.")
        return value


class BusinessReplySerializer(serializers.ModelSerializer):
    """Biznes egasi sharhga javob qoldiradi."""

    class Meta:
        model = Review
        fields = ["reply"]

    def validate_reply(self, value):
        if not value.strip():
            raise serializers.ValidationError("Javob bo'sh bo'lishi mumkin emas.")
        return value.strip()


class ProductRatingSummarySerializer(serializers.Serializer):
    """Mahsulot reytingi xulosasi — GET /reviews/summary/?product=<id>"""

    product_id = serializers.IntegerField()
    avg_rating = serializers.FloatField()
    review_count = serializers.IntegerField()
    rating_breakdown = serializers.DictField(child=serializers.IntegerField())
    verified_count = serializers.IntegerField()
