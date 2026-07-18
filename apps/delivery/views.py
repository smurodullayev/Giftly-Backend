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


class DeliveryZoneViewSet(viewsets.ModelViewSet):
    """
    /api/v1/delivery/zones/

    O'qish — hammaga.
    Yaratish / tahrirlash / o'chirish — faqat admin.

    Asosiy endpoint:
    POST /api/v1/delivery/calculate/  → narx hisoblash
    """

    queryset = DeliveryZone.objects.filter(is_active=True).order_by("sort_order", "name")
    serializer_class = DeliveryZoneSerializer
    search_fields = ["name"]
    ordering_fields = ["name", "base_fee", "sort_order"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def get_queryset(self):
        # Admin nofaol zonalarni ham ko'radi
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
        """
        POST /api/v1/delivery/zones/calculate/
        Yetkazib berish narxini hisoblaydi.

        Misol so'rov:
        {
          "destination_address": "Samarqand viloyati, Urgut tumani",
          "weight_grams": 1500,
          "order_amount": 200000
        }

        Misol javob:
        {
          "zone_name": "Viloyatlar",
          "zone_id": 2,
          "weight_grams": 1500,
          "weight_kg": 1.5,
          "base_fee": 25000,
          "per_kg_fee": 3000,
          "delivery_fee": 29500,
          "is_free": false,
          "free_above_amount": 500000
        }
        """
        serializer = DeliveryCalculateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = calculate_delivery(
            destination_address=serializer.validated_data["destination_address"],
            weight_grams=serializer.validated_data.get("weight_grams", 0),
            order_amount=serializer.validated_data.get("order_amount"),
        )

        out = DeliveryCalculateResultSerializer(result)
        status_code = (
            status.HTTP_200_OK
            if result.get("zone_id")
            else status.HTTP_404_NOT_FOUND
        )
        return Response(out.data, status=status_code)
