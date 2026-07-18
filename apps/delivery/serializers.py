from decimal import Decimal

from rest_framework import serializers

from .models import DeliveryZone


class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = [
            "id", "name", "keywords",
            "base_fee", "per_kg_fee",
            "free_above_amount",
            "is_default", "is_active", "sort_order",
        ]


class DeliveryCalculateSerializer(serializers.Serializer):
    """
    POST /api/v1/delivery/calculate/
    Yetkazib berish narxini hisoblash uchun kirish ma'lumotlari.
    """

    destination_address = serializers.CharField(
        max_length=500,
        help_text="Xaridor manzili — shahar/viloyat nomi bo'lishi shart. Masalan: 'Toshkent, Yunusobod'",
    )
    weight_grams = serializers.IntegerField(
        min_value=0,
        default=0,
        help_text="Mahsulot og'irligi grammda. 0 bo'lsa faqat base_fee qo'llanadi.",
    )
    order_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
        help_text="Buyurtma summasi — bepul yetkazish limitini tekshirish uchun (ixtiyoriy).",
    )


class DeliveryCalculateResultSerializer(serializers.Serializer):
    """Yetkazib berish hisob-kitob natijasi."""

    zone_name = serializers.CharField(allow_null=True)
    zone_id = serializers.IntegerField(allow_null=True)
    weight_grams = serializers.IntegerField()
    weight_kg = serializers.FloatField()
    base_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    per_kg_fee = serializers.DecimalField(max_digits=8, decimal_places=2)
    delivery_fee = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_free = serializers.BooleanField()
    free_above_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True
    )
    error = serializers.CharField(required=False, allow_null=True)
