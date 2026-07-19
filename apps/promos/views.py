from drf_spectacular.utils import extend_schema, extend_schema_view
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


@extend_schema_view(
    list=extend_schema(tags=["Promos"], summary="List coupons"),
    retrieve=extend_schema(tags=["Promos"], summary="Retrieve a coupon"),
    create=extend_schema(tags=["Promos"], summary="Create a coupon"),
    update=extend_schema(tags=["Promos"], summary="Update a coupon"),
    partial_update=extend_schema(tags=["Promos"], summary="Partially update a coupon"),
    destroy=extend_schema(tags=["Promos"], summary="Delete a coupon"),
)
class CouponViewSet(viewsets.ModelViewSet):
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

    @extend_schema(tags=["Promos"], summary="List usages of a coupon")
    @action(detail=True, methods=["get"], url_path="usages")
    def usages(self, request, pk=None):
        coupon = self.get_object()
        qs = CouponUsage.objects.filter(coupon=coupon).select_related("user")
        serializer = CouponUsageSerializer(qs, many=True)
        return Response(serializer.data)


@extend_schema_view(
    create=extend_schema(tags=["Promos"], summary="Apply a coupon code"),
)
class CouponApplyView(viewsets.ViewSet):
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
