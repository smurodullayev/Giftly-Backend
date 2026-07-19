from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view
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


@extend_schema_view(
    list=extend_schema(
        tags=["Delivery"],
        summary="List delivery zones",
        description=(
            "Returns all active delivery zones sorted by priority. "
            "Admin users also see inactive zones."
        ),
    ),
    retrieve=extend_schema(
        tags=["Delivery"],
        summary="Retrieve a delivery zone",
        description="Returns full details of a single delivery zone by ID.",
    ),
    create=extend_schema(
        tags=["Delivery"],
        summary="Create a delivery zone",
        description="Admin only. Creates a new delivery zone with keywords and fee rules.",
    ),
    update=extend_schema(
        tags=["Delivery"],
        summary="Update a delivery zone",
        description="Admin only. Fully replaces all fields of a delivery zone.",
    ),
    partial_update=extend_schema(
        tags=["Delivery"],
        summary="Partially update a delivery zone",
        description="Admin only. Updates only the provided fields.",
    ),
    destroy=extend_schema(
        tags=["Delivery"],
        summary="Delete a delivery zone",
        description="Admin only. Permanently removes a delivery zone.",
    ),
)
class DeliveryZoneViewSet(viewsets.ModelViewSet):
    """
    /api/v1/delivery/zones/

    Read — public.
    Create / update / delete — admin only.
    """

    queryset          = DeliveryZone.objects.filter(is_active=True).order_by("sort_order", "name")
    serializer_class  = DeliveryZoneSerializer
    search_fields     = ["name"]
    ordering_fields   = ["name", "base_fee", "sort_order"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [IsAdminRole()]

    def get_queryset(self):
        qs = DeliveryZone.objects.order_by("sort_order", "name")
        if self.request.user.is_authenticated and self.request.user.role == "admin":
            return qs
        return qs.filter(is_active=True)

    @extend_schema(
        tags=["Delivery"],
        summary="Calculate delivery fee",
        description=(
            "Calculates the delivery fee for a given address and order details. "
            "Matches the address against zone keywords (case-insensitive). "
            "Returns `404` if no matching zone is found."
        ),
        request=DeliveryCalculateSerializer,
        responses={
            200: DeliveryCalculateResultSerializer,
            404: OpenApiResponse(description="No delivery zone matched the address."),
        },
        examples=[
            OpenApiExample(
                name="Regional city",
                request_only=True,
                value={
                    "destination_address": "Samarqand viloyati, Urgut tumani",
                    "weight_grams": 1500,
                    "order_amount": 200000,
                },
            ),
            OpenApiExample(
                name="Fee calculated",
                response_only=True,
                status_codes=["200"],
                value={
                    "zone_name": "Viloyatlar",
                    "zone_id": 2,
                    "weight_grams": 1500,
                    "weight_kg": 1.5,
                    "base_fee": 25000,
                    "per_kg_fee": 3000,
                    "delivery_fee": 29500,
                    "is_free": False,
                    "free_above_amount": 500000,
                },
            ),
        ],
    )
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
            status.HTTP_200_OK
            if result.get("zone_id")
            else status.HTTP_404_NOT_FOUND
        )
        return Response(out.data, status=status_code)
