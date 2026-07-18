from rest_framework import serializers

from .models import Category, Occasion, Product, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class OccasionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occasion
        fields = ["id", "name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class ProductImageSerializer(serializers.SerializerMethodField):
    """Mahsulot rasmlari — MediaFile dan olinadi."""
    pass


class ProductReadSerializer(serializers.ModelSerializer):
    """GET so'rovlari uchun — nested ma'lumotlar va rasmlar."""

    category = CategorySerializer(read_only=True)
    occasions = OccasionSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    business_username = serializers.CharField(source="business.username", read_only=True)
    images = serializers.SerializerMethodField()
    effective_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "slug", "business", "business_username",
            "title", "description",
            "price", "sale_price", "effective_price",
            "category", "occasions", "tags",
            "sku", "stock", "min_order_qty", "is_in_stock",
            "weight_grams",
            "images",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = fields

    def get_images(self, obj) -> list:
        """Mahsulotga bog'liq MediaFile larni qaytaradi."""
        from django.contrib.contenttypes.models import ContentType
        from apps.media.models import MediaFile
        from apps.media.serializers import MediaFileSerializer
        ct = ContentType.objects.get_for_model(obj)
        images = (
            MediaFile.objects
            .filter(content_type=ct, object_id=obj.pk, purpose="product_image")
            .order_by("order", "-is_primary", "created_at")
        )
        return MediaFileSerializer(
            images, many=True, context=self.context
        ).data


class ProductWriteSerializer(serializers.ModelSerializer):
    """POST / PATCH so'rovlari uchun — business token dan avtomatik o'rnatiladi."""

    class Meta:
        model = Product
        fields = [
            "title", "description",
            "price", "sale_price",
            "category", "occasions", "tags",
            "sku", "stock", "min_order_qty",
            "weight_grams",
            "is_active",
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Narx 0 dan katta bo'lishi kerak.")
        return value

    def validate_sale_price(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Chegirma narxi 0 dan katta bo'lishi kerak.")
        return value

    def validate(self, attrs):
        price = attrs.get("price") or (self.instance.price if self.instance else None)
        sale_price = attrs.get("sale_price")
        if sale_price and price and sale_price >= price:
            raise serializers.ValidationError(
                {"sale_price": "Chegirma narxi asosiy narxdan kichik bo'lishi kerak."}
            )
        return attrs

    def create(self, validated_data):
        validated_data["business"] = self.context["request"].user
        return super().create(validated_data)
