from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Coupon, CouponUsage
from .serializers import (
    CouponApplyResultSerializer,
    CouponApplySerializer,
    CouponSerializer,
    CouponUsageSerializer,
)


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class CouponViewSet(viewsets.ModelViewSet):
    """
    /api/v1/promos/coupons/

    CRUD — faqat admin.
    GET    /promos/coupons/              → ro'yxat
    POST   /promos/coupons/              → yaratish
    PATCH  /promos/coupons/{id}/         → tahrirlash
    DELETE /promos/coupons/{id}/         → o'chirish

    GET    /promos/coupons/{id}/usages/  → kupon ishlatilish tarixi

    Barcha foydalanuvchilar uchun:
    POST   /promos/apply/                → kodni tekshirish va chegirma hisoblash
    """

    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAdminRole]
    search_fields = ["code", "description"]
    ordering_fields = ["created_at", "valid_until", "used_count"]
    ordering = ["-created_at"]
    filterset_fields = {
        "is_active": ["exact"],
        "discount_type": ["exact"],
    }

    @action(detail=True, methods=["get"], url_path="usages")
    def usages(self, request, pk=None):
        """GET /promos/coupons/{id}/usages/ — kupon kimlar tomonidan ishlatilgan."""
        coupon = self.get_object()
        qs = CouponUsage.objects.filter(coupon=coupon).select_related("user")
        serializer = CouponUsageSerializer(qs, many=True)
        return Response(serializer.data)


class CouponApplyView(viewsets.ViewSet):
    """
    POST /api/v1/promos/apply/
    Kuponni tekshirish va chegirma summasini hisoblash.
    Buyurtma yaratilmaydi — faqat hisob-kitob.

    Body:
      { "code": "YOZGI25", "order_amount": 250000 }

    Javob:
      {
        "code": "YOZGI25",
        "discount_type": "percent",
        "discount_value": 25,
        "order_amount": 250000,
        "discount_amount": 62500,
        "final_amount": 187500
      }
    """

    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = CouponApplySerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        coupon = serializer.validated_data["coupon"]
        order_amount = serializer.validated_data["order_amount"]
        discount = coupon.calculate_discount(order_amount)

        result = CouponApplyResultSerializer({
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "order_amount": order_amount,
            "discount_amount": discount,
            "final_amount": order_amount - discount,
        })
        return Response(result.data, status=status.HTTP_200_OK)
