from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DeliveryZone
from .serializers import (
    DeliveryCalculateResultSerializer,
    DeliveryCalculateSerializer,
    DeliveryZoneSerializer,
)
from .services import calculate_delivery


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


@extend_schema(tags=["Delivery"])
class DeliveryZoneViewSet(viewsets.ModelViewSet):
    queryset         = DeliveryZone.objects.filter(is_active=True).order_by("sort_order", "name")
    serializer_class = DeliveryZoneSerializer
    search_fields    = ["name"]
    ordering_fields  = ["name", "base_fee", "sort_order"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def get_queryset(self):
        qs = DeliveryZone.objects.order_by("sort_order", "name")
        if self.request.user.is_authenticated and self.request.user.role == "admin":
            return qs
        return qs.filter(is_active=True)

    @action(
        detail=False,
        methods=["post"],
        url_path="calculate",
        permission_classes=[permissions.AllowAny],
    )
    def calculate(self, request):
        serializer = DeliveryCalculateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = calculate_delivery(
            destination_address=serializer.validated_data["destination_address"],
            weight_grams=serializer.validated_data.get("weight_grams", 0),
            order_amount=serializer.validated_data.get("order_amount"),
        )

        out = DeliveryCalculateResultSerializer(result)
        status_code = (
            status.HTTP_200_OK if result.get("zone_id") else status.HTTP_404_NOT_FOUND
        )
        return Response(out.data, status=status_code)
