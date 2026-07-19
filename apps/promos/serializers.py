from decimal import Decimal
from typing import Optional

from rest_framework import serializers

from .models import Coupon, CouponUsage


class CouponSerializer(serializers.ModelSerializer):
    """Admin uchun — to'liq kupon ma'lumoti."""

    is_expired = serializers.SerializerMethodField()
    remaining_uses = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            "id", "code", "description",
            "discount_type", "discount_value", "max_discount_amount",
            "min_order_amount",
            "max_uses", "used_count", "remaining_uses",
            "one_per_user",
            "valid_from", "valid_until", "is_active",
            "is_expired",
            "created_at",
        ]
        read_only_fields = ["used_count", "created_at"]

    def get_is_expired(self, obj) -> bool:
        from django.utils import timezone
        if obj.valid_until:
            return timezone.now() > obj.valid_until
        return False

    def get_remaining_uses(self, obj) -> Optional[int]:
        if obj.max_uses is None:
            return None
        return max(0, obj.max_uses - obj.used_count)

    def validate(self, attrs):
        discount_type = attrs.get("discount_type", getattr(self.instance, "discount_type", None))
        discount_value = attrs.get("discount_value", getattr(self.instance, "discount_value", None))

        if discount_type == Coupon.DiscountType.PERCENT and discount_value and discount_value > 100:
            raise serializers.ValidationError(
                {"discount_value": "Foiz chegirma 100% dan oshmasligi kerak."}
            )

        valid_from = attrs.get("valid_from")
        valid_until = attrs.get("valid_until")
        if valid_from and valid_until and valid_until <= valid_from:
            raise serializers.ValidationError(
                {"valid_until": "Tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak."}
            )

        return attrs

    def validate_code(self, value):
        return value.upper().strip()


class CouponApplySerializer(serializers.Serializer):
    """
    Kupon qo'llash uchun — POST /promos/apply/
    Chegirma summasini hisoblaydi, ammo hali ishlatilgan deb hisoblamaydi.
    """

    code = serializers.CharField(max_length=50)
    order_amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_code(self, value):
        return value.upper().strip()

    def validate(self, attrs):
        code = attrs["code"]
        order_amount = attrs["order_amount"]
        user = self.context["request"].user

        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError({"code": "Bunday kupon mavjud emas."})

        is_valid, error = coupon.is_valid(user=user, order_amount=order_amount)
        if not is_valid:
            raise serializers.ValidationError({"code": error})

        attrs["coupon"] = coupon
        return attrs


class CouponApplyResultSerializer(serializers.Serializer):
    """Kupon qo'llash natijasi."""

    code = serializers.CharField()
    discount_type = serializers.CharField()
    discount_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    final_amount = serializers.DecimalField(max_digits=12, decimal_places=2)


class CouponUsageSerializer(serializers.ModelSerializer):
    """Kupon ishlatilish tarixi."""

    user_username = serializers.CharField(source="user.username", read_only=True)
    coupon_code = serializers.CharField(source="coupon.code", read_only=True)

    class Meta:
        model = CouponUsage
        fields = [
            "id", "coupon", "coupon_code",
            "user", "user_username",
            "order_amount", "discount_applied",
            "used_at",
        ]
        read_only_fields = fields
